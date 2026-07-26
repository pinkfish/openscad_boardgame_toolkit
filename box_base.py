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
from dataclasses import dataclass
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
    Lid,
)
from labels import MakeLabelOptions


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


class Label:
    """A label to be placed on a lid, created by :meth:`Box.make_label`.

    All styling fields (:attr:`font`, :attr:`border`, :attr:`radius`, etc.)
    are class variables with sensible defaults — set them on the instance to
    customise.  :meth:`build` creates the actual label solid using dimensions
    provided by the Box at creation time.

    Usage::

        label = Label("Frogs")
        label = Label("Snakes", font="Stencil Std:style=Bold", label_type=LabelType.FRAMELESS)

        lid = box.create_lid(Lid(lid_thickness=2, label=Label("Trains"), shape_options=MakeShapeObject()))
    """

    text: str
    position: list[float] | None = None
    size: list[float] | None = None

    text_scale: float = 1.0
    text_length: float | None = None
    angle: float | None = 0
    label_colour: str = default_label_colour
    label_background_colour: str = default_label_background_colour
    short_length: bool = False
    label_diff: list[float] = None  # type: ignore[assignment] -- initialised in __init__
    border: float = 2
    offset: float = 4
    radius: float = 5
    font: str = default_label_font
    full_height: bool = False
    finger_hole_size: float | None = 10
    material_colour: str = default_material_colour
    label_type: LabelType = default_label_type
    solid_background: bool = default_label_solid_background

    def __init__(self, text: str, **kwargs: object) -> None:
        self.text = text
        self.label_diff = [0, 0]
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise TypeError(f"Label() got an unexpected keyword argument '{k}'")

    def build(
        self,
        *,
        lid_thickness: float,
        material_colour: str,
        inner_width: float,
        inner_length: float,
        wall_thickness: float,
    ) -> Bosl2Solid | None:
        """Create the label solid using the provided box dimensions.

        Args:
            lid_thickness: thickness of the lid
            material_colour: box material colour (used if the label doesn't set its own)
            inner_width: clear interior width of the box
            inner_length: clear interior length of the box
            wall_thickness: box wall thickness (for default positioning)
        """
        from lids_base import MakeLidLabel

        options = MakeLabelOptions(
            text_scale=self.text_scale,
            text_length=self.text_length,
            angle=self.angle,
            label_colour=self.label_colour,
            label_background_colour=self.label_background_colour,
            short_length=self.short_length,
            label_diff=list(self.label_diff),
            border=self.border,
            offset=self.offset,
            radius=self.radius,
            font=self.font,
            full_height=self.full_height,
            finger_hole_size=self.finger_hole_size,
            material_colour=material_colour if self.material_colour == default_material_colour else self.material_colour,
            label_type=self.label_type,
            solid_background=self.solid_background,
        )

        calc_size = list(self.size) if self.size else [inner_width, inner_length]
        calc_pos = list(self.position) if self.position else [wall_thickness / 2, wall_thickness / 2, 0]

        piece = MakeLidLabel(
            size=calc_size,
            lid_thickness=lid_thickness,
            text_str=self.text,
            options=options,
        )
        if piece is not None:
            return piece.translate(calc_pos)
        return None


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

        lid = box.create_lid(Lid(lid_thickness=2, label=Label("Trains"), shape_options=MakeShapeObject()))
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

    def create_lid(self, lid: Lid | None = None) -> Bosl2Solid:
        """Create the lid for this box.

        Builds the base lid body via :meth:`_make_base_lid`, then applies
        shape pattern, label, and fingernail from *lid*, and stacks with
        :func:`~lids_base.internal_build_lid`.

        Subclasses override :meth:`_make_base_lid` and :meth:`_lid_adjustment`
        to provide their specific lid geometry.
        """
        l = lid if lid is not None else Lid(lid_thickness=self.lid_thickness)
        l.lid_thickness = l.lid_thickness or self.lid_thickness
        l.material_colour = l.material_colour or self.material_colour
        if l.size is None:
            l.size = [self.inner_width, self.inner_length]
        if l.fingernail and l.fingernail_width is None:
            l.fingernail_width = self.inner_width
            l.fingernail_length = self.inner_length

        base_body = self._make_base_lid(l.lid_rounding)
        overlay = self._lid_overlay(l)
        children = [base_body] + overlay
        stack = internal_build_lid(
            lid_thickness=l.lid_thickness,
            children=children,
            size_spacing=self.size_spacing,
        )
        return self._lid_adjustment(stack)

    def _make_base_lid(self, lid_rounding: float | None = None) -> Bosl2Solid:
        """Build the raw lid body. Subclasses MUST override for box-specific geometry."""
        return bosl2.shapes3d.cuboid(
            [self.inner_width, self.inner_length, self.lid_thickness],
            anchor=BOTTOM + FRONT + LEFT,
        ).color(self.material_colour)

    def _lid_overlay(self, lid: Lid) -> list:
        """Build the list of overlay children by delegating to :meth:`Lid.overlay`."""
        return lid.overlay(label_builder=self.make_label)

    def _lid_adjustment(self, stack: Bosl2Solid) -> Bosl2Solid:
        """Post-process the assembled lid stack. Subclasses MAY override."""
        return stack

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

    def make_label(self, label: Label) -> Bosl2Solid | None:
        """Create a label solid from *label*, using the Box's dimensions and colour.

        Delegates to :meth:`Label.build`, passing the Box's lid thickness,
        material colour, interior dimensions, and wall thickness.
        """
        return label.build(
            lid_thickness=self.lid_thickness,
            material_colour=self.material_colour,
            inner_width=self.inner_width,
            inner_length=self.inner_length,
            wall_thickness=self.wall_thickness,
        )

    # ------------------------------------------------------------------
    # Lid composition helper
    # ------------------------------------------------------------------

    def _compose_lid(
        self,
        lid_body: Bosl2Solid,
        *,
        lid: "Lid | None" = None,
        label: Label | None = None,
        extra_children: list | None = None,
        fingernail: bool = False,
    ) -> Bosl2Solid:
        """Assemble a complete lid from *lid_body* plus optional mesh, label, fingernail.

        Args:
            lid_body: the raw lid solid (from e.g. _build_lid_body)
            lid: :class:`~lids_base.Lid` with shape mesh configuration
            label: optional :class:`Label` to overlay
            extra_children: additional solids to embed
            fingernail: if True, add a fingernail cutout
        """
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

        if lid is not None:
            lid.material_colour = self.material_colour
            lid.lid_thickness = self.lid_thickness
            if lid.size is None:
                lid.size = [self.inner_width, self.inner_length]
            mesh = lid.build()
            if mesh is not None:
                children.append(mesh)

        if label is not None:
            label_shape = self.make_label(label)
            if label_shape is not None:
                children.append(label_shape)

        if extra_children:
            children.extend(extra_children)

        if children:
            return internal_build_lid(
                lid_thickness=self.lid_thickness,
                children=[lid_body] + children,
                size_spacing=self.size_spacing,
            )
        return lid_body
