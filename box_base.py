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
from components import FingerHoleWall
from lids_base import internal_build_lid, MakeLidLabel, LidMeshBasic, SlidingLidFingernail, IsDenseShapeType, DenseShapeEdges
from labels import MakeLabelOptions, LabelOptions
from shape_type import MakeShapeObject, ShapeObject, ShapeByType, ShapeNeedsInnerControl


class FingerHoleLocation(IntEnum):
    """Which side of the box a finger hole is placed on."""
    LEFT = 0
    RIGHT = 1
    FRONT = 2
    BACK = 3


class Box(Bosl2Solid):
    """Base class for all board game toolkit box types.

    Subclasses override :meth:`_build_box_body`, :meth:`create_lid`, and
    :meth:`inside_mask` to provide their specific geometry.  Shared features
    -- children carving, finger holes, label/shape handling, MMU support,
    and BOSL2 positioning -- are handled here.
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
    ):
        assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be [x,y,z], size={size}"

        self._size = list(size)
        self.wall_thickness = wall_thickness if wall_thickness is not None else default_wall_thickness
        self.floor_thickness = floor_thickness if floor_thickness is not None else default_floor_thickness
        self.lid_thickness = lid_thickness if lid_thickness is not None else default_lid_thickness
        self.size_spacing = size_spacing if size_spacing is not None else m_piece_wiggle_room
        self.material_colour = material_colour if material_colour is not None else default_material_colour
        self.positive_colour = positive_colour if positive_colour is not None else default_positive_colour
        self.anchor = Vec3(anchor) if anchor is not None else BOTTOM + FRONT + LEFT
        self.orient = orient if orient is not None else TOP
        self.spin = spin
        self._children = list(children) if children else []
        self._positive_only_children = list(positive_only_children) if positive_only_children else []
        self._positive_negative_children = list(positive_negative_children) if positive_negative_children else []

        self._finger_holes = finger_holes or []
        self._finger_hole_radius = finger_hole_radius if finger_hole_radius is not None else 14
        self._finger_hole_height = finger_hole_height
        self._finger_hole_depth = finger_hole_depth if finger_hole_depth is not None else 6
        self._finger_hole_rounding_radius = finger_hole_rounding_radius if finger_hole_rounding_radius is not None else 3
        self._finger_hole_rounding_edge = finger_hole_rounding_edge

        body = self._build_box_body()
        body = self._carve_children(body)
        body = self._apply_finger_holes(body)
        body = self._apply_mmu(body)
        body = self._apply_positioning(body)

        super().__init__(shape=body, size=size, anchor=self.anchor)

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
        """Clear interior width between the walls."""
        return self.width - self.wall_thickness * 2

    @property
    def inner_length(self) -> float:
        """Clear interior length between the walls."""
        return self.length - self.wall_thickness * 2

    @property
    def inner_height(self) -> float:
        """Clear interior floor-to-lid height."""
        return self.height - self.lid_thickness - self.floor_thickness

    # ------------------------------------------------------------------
    # Virtual methods -- override in subclasses
    # ------------------------------------------------------------------

    def _build_box_body(self) -> "PyOpenSCAD":
        """Build the raw box-body solid (before children / finger holes / MMU / positioning).

        The default creates a simple rounded cuboid, suitable for a basic
        no-lid box.  Subclasses override this for sliding-lid, hinge, etc.
        """
        body = bosl2.shapes3d.cuboid(
            [self.width, self.length, self.height],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=self.wall_thickness,
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
        )
        return body.color(self.material_colour)

    def create_lid(self) -> Bosl2Solid:
        """Create the lid for this box.  Subclasses MUST override."""
        raise NotImplementedError(f"{type(self).__name__}.create_lid()")

    def inside_mask(self) -> Bosl2Solid:
        """Return a solid representing the interior cavity (for carving children after init)."""
        return bosl2.shapes3d.cuboid(
            [self.inner_width, self.inner_length, self.inner_height],
            anchor=BOTTOM + FRONT + LEFT,
        ).translate([self.wall_thickness, self.wall_thickness, self.floor_thickness])

    # ------------------------------------------------------------------
    # Children
    # ------------------------------------------------------------------

    def _resolve_child(self, child: "PyOpenSCAD | Callable", inner_w: float, inner_l: float, inner_h: float) -> "PyOpenSCAD":
        return child(inner_w, inner_l, inner_h) if callable(child) else child

    def _carve_children(self, body: "PyOpenSCAD") -> "PyOpenSCAD":
        """Subtract each non-positive-only child from the interior."""
        kids = self._children
        result = body
        for i, c in enumerate(kids):
            if i not in self._positive_only_children:
                piece = self._resolve_child(c, self.inner_width, self.inner_length, self.inner_height)
                result = result - piece.translate([self.wall_thickness, self.wall_thickness, self.floor_thickness])
        return result

    # ------------------------------------------------------------------
    # Finger holes
    # ------------------------------------------------------------------

    def _make_finger_hole_cutter(
        self,
        location: FingerHoleLocation,
        offset: float = 0,
        radius: float | None = None,
        height: float | None = None,
        depth: float | None = None,
        rounding_radius: float | None = None,
        rounding_edge: float = 0,
    ) -> "PyOpenSCAD":
        """Return a finger-hole cutout positioned on *location* at *offset* from center.

        Args:
            location: which side (LEFT, RIGHT, FRONT, BACK)
            offset: displacement from the center of the side (mm)
            radius: hole radius (default self._finger_hole_radius)
            height: hole height (default half the box height)
            depth: depth of cut (default self._finger_hole_depth)
            rounding_radius: rounding at the top (default self._finger_hole_rounding_radius)
            rounding_edge: extra edge rounding (default 0)
        """
        r = radius if radius is not None else self._finger_hole_radius
        h = height if height is not None else (self._finger_hole_height or self.height / 2)
        d = depth if depth is not None else self._finger_hole_depth
        rr = rounding_radius if rounding_radius is not None else self._finger_hole_rounding_radius

        if location == FingerHoleLocation.LEFT:
            pos = [0, self.length / 2 + offset, self.height / 2]
            orient = RIGHT
        elif location == FingerHoleLocation.RIGHT:
            pos = [self.width, self.length / 2 + offset, self.height / 2]
            orient = LEFT
        elif location == FingerHoleLocation.FRONT:
            pos = [self.width / 2 + offset, 0, self.height / 2]
            orient = BACK
        elif location == FingerHoleLocation.BACK:
            pos = [self.width / 2 + offset, self.length, self.height / 2]
            orient = FRONT
        else:
            raise ValueError(f"Unknown finger hole location: {location}")

        hole = FingerHoleWall(
            radius=r, height=h, depth_of_hole=d, rounding_radius=rr,
            rounding_edge=rounding_edge, orient=orient,
        )
        return hole.translate(pos)

    def _apply_finger_holes(self, body: "PyOpenSCAD") -> "PyOpenSCAD":
        result = body
        for hole_spec in self._finger_holes:
            if isinstance(hole_spec, tuple):
                loc, offset = hole_spec[0], hole_spec[1] if len(hole_spec) > 1 else 0
            else:
                loc, offset = hole_spec, 0
            result = result - self._make_finger_hole_cutter(loc, offset)
        return result

    # ------------------------------------------------------------------
    # MMU
    # ------------------------------------------------------------------

    def _apply_mmu(self, body: "PyOpenSCAD") -> "PyOpenSCAD":
        """Union positive-coloured copies of marked children when MAKE_MMU is active."""
        result = body
        if len(self._positive_only_children) > 0 or (len(self._positive_negative_children) > 0 and MAKE_MMU == 1):
            extra_indices = list(self._positive_only_children) + (list(self._positive_negative_children) if MAKE_MMU == 1 else [])
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

    def _apply_positioning(self, body: "PyOpenSCAD") -> "PyOpenSCAD":
        """Apply BOSL2 spin/anchor/orient positioning."""
        tmat = bosl2.transforms.reorient(
            anchor=self.anchor, spin=self.spin, orient=self.orient,
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
        """Create a label and position it on *lid*.

        Args:
            lid: the lid Bosl2Solid to attach the label to
            text_str: label text string
            label_options: :class:`~labels.LabelOptions` (default from MakeLabelOptions)
            label_size: [width, length] area for the label (default inner width × inner length)
            position: [x, y, z] offset for the label (default [wall_thickness/2, wall_thickness/2, 0])
        Returns:
            *lid* with the label carved/added as appropriate.
        """
        opts = label_options if label_options is not None else MakeLabelOptions(material_colour=self.material_colour)
        label_opts = copy.copy(opts)
        label_opts.full_height = True

        if label_size is None:
            label_size = [self.inner_width, self.inner_length]

        label_shape = MakeLidLabel(
            size=label_size, lid_thickness=self.lid_thickness,
            text_str=text_str, options=label_opts,
        )
        if label_shape is not None:
            pos = position if position is not None else [self.wall_thickness / 2, self.wall_thickness / 2, 0]
            return lid | label_shape.translate(pos)
        return lid

    # ------------------------------------------------------------------
    # Shape pattern creation
    # ------------------------------------------------------------------

    def shape_on_lid(
        self,
        lid: Bosl2Solid,
        shape_options: ShapeObject | None = None,
        shape_child: "PyOpenSCAD | None" = None,
        lid_boundary: float = 10,
        layout_width: float | None = None,
        aspect_ratio: float | None = None,
        dense: bool = False,
        dense_shape_edges: int = 6,
        inner_control: int = 0,
        position: list[float] | None = None,
    ) -> Bosl2Solid:
        """Create a repeating shape pattern and overlay it on *lid*.

        If *shape_child* is given it is used directly; otherwise *shape_options*
        determines the shape via :func:`~shape_type.ShapeByType`.

        Returns *lid* with the pattern added.
        """
        if shape_child is None:
            if shape_options is None:
                shape_options = MakeShapeObject()
            piece_raw = ShapeByType(options=shape_options)
            assert piece_raw is not None, "shape_options must not resolve to ShapeType.NONE"
            shape_child = piece_raw.color(self.material_colour)

        if layout_width is None:
            layout_width = default_lid_layout_width
        if aspect_ratio is None:
            aspect_ratio = default_lid_aspect_ratio

        mesh = LidMeshBasic(
            size=[self.inner_width, self.inner_length],
            lid_thickness=self.lid_thickness,
            boundary=lid_boundary,
            layout_width=layout_width,
            aspect_ratio=aspect_ratio,
            dense=dense,
            dense_shape_edges=dense_shape_edges,
            material_colour=self.material_colour,
            inner_control=inner_control,
            children=shape_child,
        )

        pos = position if position is not None else [self.wall_thickness, self.wall_thickness, 0]
        return lid | mesh.translate(pos)

    # ------------------------------------------------------------------
    # Lid composition helper -- assembles a lid with label + shape + fingernail
    # ------------------------------------------------------------------

    def _compose_lid(
        self,
        lid_body: "PyOpenSCAD",
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
    ) -> "PyOpenSCAD":
        """Assemble a complete lid from the base *lid_body* plus optional label, shape, fingernail."""
        children = []

        if fingernail:
            fn = bosl2.shapes3d.cuboid(
                [self.inner_width, self.inner_length, self.lid_thickness],
                anchor=BOTTOM + FRONT + LEFT,
            ).color(self.material_colour) & SlidingLidFingernail(
                self.lid_thickness, material_colour=self.material_colour,
            ).translate([self.width / 2 - self.wall_thickness / 2, self.length - self.wall_thickness - 3, 0]).shape
            children.append(fn)

        if shape_child is not None or shape_options is not None:
            mesh = LidMeshBasic(
                size=[self.inner_width, self.inner_length],
                lid_thickness=self.lid_thickness,
                boundary=lid_boundary,
                layout_width=layout_width,
                aspect_ratio=aspect_ratio if aspect_ratio is not None else default_lid_aspect_ratio,
                dense=lid_pattern_dense,
                dense_shape_edges=lid_dense_shape_edges,
                material_colour=self.material_colour,
                inner_control=pattern_inner_control,
                children=shape_child if shape_child is not None else (
                    ShapeByType(options=shape_options or MakeShapeObject()).color(self.material_colour)
                ),
            )
            children.append(mesh)

        if text_str is not None:
            opts = label_options if label_options is not None else MakeLabelOptions(material_colour=self.material_colour)
            label_opts = copy.copy(opts)
            label_shape = MakeLidLabel(
                size=[self.inner_width, self.inner_length],
                lid_thickness=self.lid_thickness,
                text_str=text_str, options=label_opts,
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
