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

# LibFile: box_base.py
#    Base Box class that all box types inherit from.
#
# FileSummary: Base box type for building boxes.
# FileGroup: Basics

from __future__ import annotations
import copy
from dataclasses import dataclass, field
from enum import IntEnum

import numpy as np
from pythonscad import *
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401

from base_bgtk import *
import bosl2.shapes3d
import bosl2.transforms
from bosl2.shapes3d import Bosl2Solid
from components import FingerHoleWall, FingerHoleBase
from lids_base import (
    internal_build_lid,
    MakeLidLabel,
    SlidingLidFingernail,
    IsDenseShapeType,
    DenseShapeEdges,
)
from labels import MakeLabelOptions, LabelOptions
from shape_type import MakeShapeObject, ShapeObject, ShapeByType, ShapeNeedsInnerControl


class FingerHoleLocation(IntEnum):
    """Which side of the box a finger hole is placed on."""

    LEFT = 0
    RIGHT = 1
    FRONT = 2
    BACK = 3


class FingerHoleType(IntEnum):
    """Kind of finger hole -- through the wall or cut into the floor."""

    WALL = 0
    FLOOR = 1


@dataclass
class FingerHole:
    """One finger-hole cutout placed on a box side.

    Usage::

        FingerHole(location=FingerHoleLocation.LEFT, offset=10)
        FingerHole(type=FingerHoleType.FLOOR, radius=12, offset=-5,
                   location=FingerHoleLocation.FRONT)
    """

    type: FingerHoleType = FingerHoleType.WALL
    location: FingerHoleLocation = FingerHoleLocation.LEFT
    offset: float = 0.0
    radius: float | None = None
    height: float | None = None
    depth: float | None = None
    rounding_radius: float | None = None
    rounding_edge: float = 0.0
    orient: list[float] | None = None


@dataclass
class LidConfig:
    """All lid pattern, label and shape parameters in one data object.

    Pass this to :meth:`Box.create_lid`. Every field has a sensible default;
    set only the ones that differ from the base lid defaults.

    Usage::

        config = LidConfig(text="Trains", shape_type=ShapeType.DENSE_HEX,
                           lid_pattern_dense=True)
        lid = box.create_lid(config)
    """

    text: str | None = None
    shape_child: "Bosl2Solid | None" = None
    shape_options: ShapeObject | None = None
    label_options: LabelOptions | None = None
    layout_width: float | None = None
    aspect_ratio: float | None = None
    lid_boundary: float = 10
    lid_rounding: float | None = None
    lid_pattern_dense: bool = False
    lid_dense_shape_edges: int = 6
    pattern_inner_control: int = 0
    extra_children: list | None = None
    fingernail: bool = False

    def apply_shape_defaults(self, shape_type: ShapeType) -> None:
        """Set pattern-related fields from *shape_type* when shape_options is a user object."""
        self.lid_pattern_dense = IsDenseShapeType(shape_type)
        self.lid_dense_shape_edges = DenseShapeEdges(shape_type)
        self.pattern_inner_control = ShapeNeedsInnerControl(shape_type)


class Box:
    """Base class for all board game toolkit box types.

    The constructor stores parameters only -- no geometry is built.
    Call :meth:`create_box` to build the box body with children,
    finger holes, MMU and final positioning.

    Subclasses override :meth:`_build_box_body`, :meth:`create_lid`, and
    :meth:`inside_mask` to provide their specific geometry.

    Usage::

        box = SlidingBox([50, 100, 30], "mybox")
        solid = box.create_box(children=[divider, cavity],
            finger_holes=[FingerHole(location=FingerHoleLocation.LEFT, offset=10),
                          FingerHole(type=FingerHoleType.FLOOR)])
        solid.show()

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
    ):
        assert label is not None, f"Need to specify a label $label"
        self.label = label
        assert isinstance(size, (list, tuple)) and len(size) == 3, f"{self.label}: size must be [x,y,z], size={size}"

        self._size = list(size)
        self.wall_thickness = wall_thickness if wall_thickness is not None else default_wall_thickness
        self.floor_thickness = floor_thickness if floor_thickness is not None else default_floor_thickness
        self.lid_thickness = lid_thickness if lid_thickness is not None else default_lid_thickness
        self.material_colour = material_colour if material_colour is not None else default_material_colour
        self.positive_colour = default_positive_colour
        self.size_spacing = m_piece_wiggle_room
        self.anchor = BOTTOM + FRONT + LEFT
        self.orient = TOP
        self.spin = 0

    # ------------------------------------------------------------------
    # Dimensions (derived and virtual)
    # ------------------------------------------------------------------

    @property
    def width(self) -> float:
        return self._size[0]

    @property
    def length(self) -> float:
        return self._size[1]

    @property
    def height(self) -> float:
        return self._size[2]

    @property
    def inner_width(self) -> float:
        return self.width - self.wall_thickness * 2

    @property
    def inner_length(self) -> float:
        return self.length - self.wall_thickness * 2

    @property
    def inner_height(self) -> float:
        return self.height - self.lid_thickness - self.floor_thickness

    # ------------------------------------------------------------------
    # Virtual methods -- override in subclasses
    # ------------------------------------------------------------------

    def _build_box_body(self) -> Bosl2Solid:
        body = bosl2.shapes3d.cuboid(
            [self.width, self.length, self.height],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=self.wall_thickness,
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
        )
        return body.color(self.material_colour)

    def create_lid(self, config: LidConfig | None = None) -> Bosl2Solid:
        """Create the lid for this box. Subclasses MUST override."""
        raise NotImplementedError(f"{self.label}.create_lid()")

    def inside_mask(self) -> Bosl2Solid:
        return bosl2.shapes3d.cuboid(
            [self.inner_width, self.inner_length, self.inner_height],
            anchor=BOTTOM + FRONT + LEFT,
        ).translate([self.wall_thickness, self.wall_thickness, self.floor_thickness])

    # ------------------------------------------------------------------
    # create_box -- finalises the box body with children / finger holes / MMU / positioning
    # ------------------------------------------------------------------

    def create_box(
        self,
        *,
        children: list[Bosl2Solid],
        positive_only_children: list[int] | None = None,
        positive_negative_children: list[int] | None = None,
        finger_holes: list[FingerHole] | None = None,
    ) -> Bosl2Solid:
        """Build and finalise the box body. Subclasses MUST override."""
        raise NotImplementedError(f"{self.label}.create_box()")

    # ------------------------------------------------------------------
    # _finish_box -- shared body-assembly pipeline (called from subclass create_box)
    # ------------------------------------------------------------------

    def _finish_box(
        self,
        body: Bosl2Solid,
        children: "list | None" = None,
        positive_only_children: list[int] | None = None,
        positive_negative_children: list[int] | None = None,
        finger_holes: list[FingerHole] | None = None,
    ) -> Bosl2Solid:
        """Apply children, finger holes, MMU and positioning to *body*, return completed solid."""
        self._children = list(children) if children else []
        self._positive_only_children = list(positive_only_children) if positive_only_children else []
        self._positive_negative_children = list(positive_negative_children) if positive_negative_children else []

        body = self._carve_children(body)
        if finger_holes:
            body = self._apply_finger_holes(body, finger_holes)
        body = self._apply_mmu(body)
        body = self._apply_positioning(body)
        self._body = body
        return body

    # ------------------------------------------------------------------
    # Children
    # ------------------------------------------------------------------

    def _resolve_child(
        self, child: "PyOpenSCAD | Callable", inner_w: float, inner_l: float, inner_h: float
    ) -> Bosl2Solid:
        return child(inner_w, inner_l, inner_h) if callable(child) else child

    def _carve_children(self, body: Bosl2Solid) -> Bosl2Solid:
        result = body
        for i, c in enumerate(self._children):
            if i not in self._positive_only_children:
                piece = self._resolve_child(c, self.inner_width, self.inner_length, self.inner_height)
                result = result - piece.translate([self.wall_thickness, self.wall_thickness, self.floor_thickness])
        return result

    # ------------------------------------------------------------------
    # Finger holes
    # ------------------------------------------------------------------

    def _make_finger_hole_cutter(self, fh: FingerHole) -> Bosl2Solid:
        """Return a finger-hole cutout positioned according to *fh*."""
        r = fh.radius if fh.radius is not None else 14
        rr = fh.rounding_radius if fh.rounding_radius is not None else 3

        if fh.type == FingerHoleType.FLOOR:
            h = fh.height if fh.height is not None else 14
            hole = FingerHoleBase(
                radius=r,
                height=h,
                rounding_radius=rr,
                wall_thickness=self.wall_thickness,
            )
            # Floor holes are placed relative to the box interior floor, offset
            # from center along the indicated wall side.
            if fh.location == FingerHoleLocation.LEFT:
                pos = [
                    0 - self.wall_thickness / 2,
                    self.length / 2 + fh.offset,
                    self.floor_thickness,
                ]
                orient = RIGHT
            elif fh.location == FingerHoleLocation.RIGHT:
                pos = [
                    self.width + self.wall_thickness / 2,
                    self.length / 2 + fh.offset,
                    self.floor_thickness,
                ]
                orient = LEFT
            elif fh.location == FingerHoleLocation.FRONT:
                pos = [
                    self.width / 2 + fh.offset,
                    0 - self.wall_thickness / 2,
                    self.floor_thickness,
                ]
                orient = BACK
            elif fh.location == FingerHoleLocation.BACK:
                pos = [
                    self.width / 2 + fh.offset,
                    self.length + self.wall_thickness / 2,
                    self.floor_thickness,
                ]
                orient = FRONT
            else:
                raise ValueError(f"{self.label}: unknown finger hole location: {fh.location}")
            return hole.translate(pos)

        # Wall type
        d = fh.depth if fh.depth is not None else 6
        h = fh.height if fh.height is not None else self.height / 2

        if fh.location == FingerHoleLocation.LEFT:
            pos = [0, self.length / 2 + fh.offset, self.height / 2]
            orient_val = RIGHT
        elif fh.location == FingerHoleLocation.RIGHT:
            pos = [self.width, self.length / 2 + fh.offset, self.height / 2]
            orient_val = LEFT
        elif fh.location == FingerHoleLocation.FRONT:
            pos = [self.width / 2 + fh.offset, 0, self.height / 2]
            orient_val = BACK
        elif fh.location == FingerHoleLocation.BACK:
            pos = [self.width / 2 + fh.offset, self.length, self.height / 2]
            orient_val = FRONT
        else:
            raise ValueError(f"{self.label}: unknown finger hole location: {fh.location}")

        hole = FingerHoleWall(
            radius=r,
            height=h,
            depth_of_hole=d,
            rounding_radius=rr,
            rounding_edge=fh.rounding_edge,
            orient=orient_val,
        )
        return hole.translate(pos)

    def _apply_finger_holes(self, body: Bosl2Solid, finger_holes: list[FingerHole]) -> Bosl2Solid:
        result = body
        for fh in finger_holes:
            result = result - self._make_finger_hole_cutter(fh)
        return result

    # ------------------------------------------------------------------
    # MMU
    # ------------------------------------------------------------------

    def _apply_mmu(self, body: Bosl2Solid) -> Bosl2Solid:
        result = body
        if len(self._positive_only_children) > 0 or (len(self._positive_negative_children) > 0 and MAKE_MMU == 1):
            extra_indices = list(self._positive_only_children) + (
                list(self._positive_negative_children) if MAKE_MMU == 1 else []
            )
            extra = None
            for i in extra_indices:
                piece = (
                    self._resolve_child(self._children[i], self.inner_width, self.inner_length, self.inner_height)
                    .color(self.positive_colour)
                    .translate([self.wall_thickness, self.wall_thickness, self.floor_thickness])
                )
                extra = piece if extra is None else extra | piece
            if extra is not None:
                result = result | extra
        return result

    # ------------------------------------------------------------------
    # Positioning
    # ------------------------------------------------------------------

    def _effective_height(self) -> float:
        return self.height

    def _apply_positioning(self, body: Bosl2Solid) -> Bosl2Solid:
        tmat = bosl2.transforms.reorient(
            anchor=self.anchor,
            spin=self.spin,
            orient=self.orient,
            size=[self.width, self.length, self._effective_height()],
        )
        return body.translate([-self.width / 2, -self.length / 2, -self.height / 2]).multmatrix(tmat)

    # ------------------------------------------------------------------
    # Label creation
    # ------------------------------------------------------------------

    def label_on_lid(
        self,
        lid: Bosl2Solid,
        text_str: str,
        label_options: LabelOptions | None = None,
        label_size: list[float] | None = None,
        position: list[float] | None = None,
    ) -> Bosl2Solid:
        opts = label_options if label_options is not None else MakeLabelOptions(material_colour=self.material_colour)
        label_opts = copy.copy(opts)
        label_opts.full_height = True

        if label_size is None:
            label_size = [self.inner_width, self.inner_length]

        label_shape = MakeLidLabel(
            size=label_size,
            lid_thickness=self.lid_thickness,
            text_str=text_str,
            options=label_opts,
        )
        if label_shape is not None:
            pos = position if position is not None else [self.wall_thickness / 2, self.wall_thickness / 2, 0]
            return lid | label_shape.translate(pos)
        return lid

    # ------------------------------------------------------------------
    # Shape fill -- delegates to LidMeshBasic for consistent grid layout
    # ------------------------------------------------------------------

    def _shape_fill(
        self,
        *,
        shape_child: PyOpenSCAD | None = None,
        shape_options: ShapeObject | None = None,
        width: float,
        length: float,
        lid_thickness: float,
        boundary: float = 10,
    ) -> Bosl2Solid | None:
        """Fill a width×length rectangle with *shape_child* or *shape_options*.

        Uses :func:`~lids_base.LidMeshBasic` for consistent grid layout
        matching the golden test images.
        """
        piece = shape_child
        if piece is None:
            if shape_options is None:
                shape_options = MakeShapeObject()
            piece = ShapeByType(options=shape_options)
        if piece is None:
            return None
        piece = piece.color(self.material_colour)

        from lids_base import LidMeshBasic

        dense = False
        dense_edges = 6
        inner_ctrl: int = 0
        layout_w = None
        if shape_options:
            dense = IsDenseShapeType(shape_options.shape_type)
            dense_edges = DenseShapeEdges(shape_options.shape_type)
            inner_ctrl = ShapeNeedsInnerControl(shape_options.shape_type)
            if shape_options.shape_width:
                layout_w = shape_options.shape_width

        return LidMeshBasic(
            size=[width, length],
            lid_thickness=lid_thickness,
            boundary=boundary,
            layout_width=layout_w,
            dense=dense,
            dense_shape_edges=dense_edges,
            material_colour=self.material_colour,
            inner_control=inner_ctrl,
            children=piece,
        )

    # ------------------------------------------------------------------
    # Lid composition helper
    # ------------------------------------------------------------------

    def _compose_lid(
        self,
        lid_body: Bosl2Solid,
        *,
        text_str: str | None = None,
        label_options: LabelOptions | None = None,
        shape_child: "PyOpenSCAD | None" = None,
        shape_options: ShapeObject | None = None,
        lid_boundary: float = 10,
        layout_width: float | None = None,
        aspect_ratio: float | None = None,
        lid_pattern_dense: bool = False,
        lid_dense_shape_edges: int = 6,
        pattern_inner_control: int = 0,
        extra_children: list | None = None,
        fingernail: bool = False,
    ) -> Bosl2Solid:
        children = []

        if fingernail:
            fn = (
                bosl2.shapes3d.cuboid(
                    [self.inner_width, self.inner_length, self.lid_thickness],
                    anchor=BOTTOM + FRONT + LEFT,
                ).color(self.material_colour)
                & SlidingLidFingernail(
                    self.lid_thickness,
                    material_colour=self.material_colour,
                ).shape
            )
            children.append(fn)

        if shape_child is not None or shape_options is not None:
            so = shape_options if shape_options is not None else MakeShapeObject()
            mesh = self._shape_fill(
                shape_child=shape_child,
                shape_options=so,
                width=self.inner_width,
                length=self.inner_length,
                lid_thickness=self.lid_thickness,
                boundary=lid_boundary,
            )
            if mesh is not None:
                children.append(mesh)

        if text_str is not None:
            opts = (
                label_options if label_options is not None else MakeLabelOptions(material_colour=self.material_colour)
            )
            label_opts = copy.copy(opts)
            label_shape = MakeLidLabel(
                size=[self.inner_width, self.inner_length],
                lid_thickness=self.lid_thickness,
                text_str=text_str,
                options=label_opts,
            )
            if label_shape is not None:
                children.append(label_shape.translate([self.wall_thickness / 2, self.wall_thickness / 2, 0]))

        if extra_children:
            children.extend(extra_children)

        if children:
            return internal_build_lid(
                lid_thickness=self.lid_thickness,
                children=[lid_body] + children,
                size_spacing=self.size_spacing,
            )
        return lid_body
