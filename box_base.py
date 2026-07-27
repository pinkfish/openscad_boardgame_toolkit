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
import types as _types
from dataclasses import dataclass, field
from enum import IntEnum

import numpy as np
from pythonscad import *
from typing import TYPE_CHECKING, Any, Callable, Union

from labels import LabelOptions
from shape_type import ShapeObject

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

# Box contents are self-describing InnerObject entries (see base_bgtk.InnerObject /
# ObjectType). They may be given directly as a list, or as a callable(InnerSize) for
# content that needs to know the box interior size.
Contents = Union[list[InnerObject], Callable[[InnerSize], list[InnerObject]]]

# Fields that can be copied from a LabelOptions object into a Label keyword-arg dict.
_LABEL_OPTION_FIELDS = (
    "text_scale", "text_length", "angle", "label_colour",
    "label_background_colour", "short_length", "label_diff",
    "border", "offset", "radius", "font", "full_height",
    "finger_hole_size", "label_type", "solid_background",
)


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
class Label:
    """A label to be placed on a lid, created by :meth:`Box.make_label`.

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
    label_colour: str = field(default_factory=lambda: default_label_colour)
    label_background_colour: str = field(default_factory=lambda: default_label_background_colour)
    short_length: bool = False
    label_diff: list[float] = field(default_factory=lambda: [0.0, 0.0])
    border: float = 2
    offset: float = 4
    radius: float = 5
    font: str = field(default_factory=lambda: default_label_font)
    full_height: bool = False
    finger_hole_size: float | None = 10
    material_colour: str = field(default_factory=lambda: default_material_colour)
    label_type: LabelType = field(default_factory=lambda: default_label_type)
    solid_background: bool = field(default_factory=lambda: default_label_solid_background)



@dataclass
class BoxSpec:
    """Complete, immutable specification for a box: dimensions, materials, contents, and lid.

    Pass a single ``BoxSpec`` to any :class:`Box` subclass constructor
    (e.g. ``SlidingBox(spec)``).  Call :meth:`~Box.make_box` and
    :meth:`~Box.make_lid` with **no arguments** to generate both parts from
    this single shared object — the box and lid are therefore guaranteed to
    have matching dimensions and thicknesses.

    Usage::

        from box_base import BoxSpec, FingerHole, FingerHoleLocation
        from sliding_box import SlidingBox

        spec = BoxSpec(
            size=[100, 60, 30],
            label="EarthCardBox",
            wall_thickness=3,
            lid_thickness=2,
            contents=lambda inner: [
                InnerObject(cube([inner.width, inner.length, inner.height]))
            ],
            finger_holes=[FingerHole(location=FingerHoleLocation.LEFT)],
            lid_label="Earth",
        )

        box = SlidingBox(spec)
        box.make_box().show()
        box.make_lid().show()
    """

    # ---- Required: identity + outer geometry ---------------------------------
    size: list[float]   # [width, length, height] outer dimensions
    label: str          # print-file / debug name for this box

    # ---- Material / thickness (all fall back to the base_bgtk global defaults) ----
    wall_thickness: float = field(default_factory=lambda: default_wall_thickness)
    floor_thickness: float = field(default_factory=lambda: default_floor_thickness)
    lid_thickness: float = field(default_factory=lambda: default_lid_thickness)
    material_colour: str = field(default_factory=lambda: default_material_colour)

    # ---- Positioning (forwarded to _apply_positioning) -----------------------
    spin: float = 0
    anchor: list[float] | None = None   # None → BOTTOM + FRONT + LEFT
    orient: list[float] | None = None   # None → TOP

    # ---- Box-type-specific options -------------------------------------------
    # SlidingBox reads ``sliding_lid_options``; other box types ignore it.
    # Construct with ``MakeSlidingLidOptions()`` from sliding_box.py.
    sliding_lid_options: Any = None

    # ---- Contents (inner compartments / inserts) -----------------------------
    contents: Contents | None = None
    finger_holes: list[FingerHole] | None = None

    # ---- Lid configuration ---------------------------------------------------
    # Use ``lid_label`` for the common case (text + default shape pattern).
    # Use ``lid`` for full control (pass a pre-built :class:`~lids_base.Lid`).
    # ``lid`` takes precedence over ``lid_label`` when both are set.
    lid_label: str | None = None              # shorthand label text for the lid
    lid: Lid | None = None                    # full Lid object (overrides lid_label)
    label_options: LabelOptions | None = None # styling for lid_label
    shape_options: ShapeObject | None = None  # lid pattern shape



class Box:
    """Base class for all board game toolkit box types.

    The constructor takes a single :class:`BoxSpec` that carries all
    configuration for the box.  No geometry is built at construction time;
    call :meth:`make_box` / :meth:`make_lid` (both with **no arguments**
    when a spec is provided) to produce the two printable parts.

    Subclasses override :meth:`_build_box_body`, :meth:`create_lid`, and
    :meth:`inside_mask` to provide their specific geometry.

    Usage::

        spec = BoxSpec(
            size=[50, 100, 30], label="mybox",
            wall_thickness=3,
            contents=lambda inner: [InnerObject(cavity)],
            finger_holes=[FingerHole(location=FingerHoleLocation.LEFT)],
            lid_label="Trains",
        )
        box = SlidingBox(spec)
        box.make_box().show()
        box.make_lid().show()
    """

    def __init__(self, spec: BoxSpec) -> None:
        assert isinstance(spec, BoxSpec), (
            f"Box expects a BoxSpec instance, got {type(spec).__name__}. "
            "Construct with BoxSpec(size=[w, l, h], label='name', ...)."
        )
        assert isinstance(spec.size, (list, tuple)) and len(spec.size) == 3, (
            f"{spec.label}: size must be [w, l, h], got {spec.size}"
        )
        self._spec = spec
        self.label = spec.label
        self._size = list(spec.size)
        self.wall_thickness = spec.wall_thickness
        self.floor_thickness = spec.floor_thickness
        self.lid_thickness = spec.lid_thickness
        self.material_colour = spec.material_colour
        self.positive_colour = default_positive_colour
        self.size_spacing = m_piece_wiggle_room
        self.anchor = spec.anchor if spec.anchor is not None else BOTTOM + FRONT + LEFT
        self.orient = spec.orient if spec.orient is not None else TOP
        self.spin = spec.spin

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

    def make_lid(self, lid: Lid | None = None) -> Bosl2Solid:
        """Make the lid for this box -- the second of the two top-level methods.

        When called with no arguments and a :class:`BoxSpec` was provided at
        construction time, the lid is built from :attr:`BoxSpec.lid` or
        :attr:`BoxSpec.lid_label` / :attr:`BoxSpec.shape_options`.
        Pass an explicit :class:`~lids_base.Lid` to override the spec.
        """
        if lid is None:
            lid = self._resolve_lid_from_spec()
        return self.create_lid(lid)

    def _resolve_lid_from_spec(self) -> Lid | None:
        """Build a :class:`~lids_base.Lid` from the :class:`BoxSpec` set at construction.

        Returns ``None`` when neither :attr:`BoxSpec.lid` nor :attr:`BoxSpec.lid_label`
        is set (the caller will fall back to a bare lid body).
        """
        spec = self._spec
        if spec.lid is not None:
            return spec.lid
        if spec.lid_label is not None:
            label_kwargs: dict[str, Any] = {"material_colour": self.material_colour}
            if spec.label_options is not None:
                for fld in _LABEL_OPTION_FIELDS:
                    v = getattr(spec.label_options, fld, None)
                    if v is not None:
                        label_kwargs[fld] = v
            lbl = Label(spec.lid_label, **label_kwargs)
            return Lid(
                lid_thickness=self.lid_thickness,
                label=lbl,
                shape_options=spec.shape_options,
                material_colour=self.material_colour,
            )
        return None

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
    # make_box -- finalises the box body with contents / finger holes / MMU / positioning
    # ------------------------------------------------------------------

    def make_box(
        self,
        *,
        contents: "Contents | None" = None,
        finger_holes: list[FingerHole] | None = None,
    ) -> Bosl2Solid:
        """Build and finalise the box body. Subclasses MUST override."""
        raise NotImplementedError(f"{self.label}.make_box()")

    def create_box(
        self,
        *,
        contents: "Contents | None" = None,
        finger_holes: list[FingerHole] | None = None,
    ) -> Bosl2Solid:
        """Backward-compatible alias for :meth:`make_box`."""
        return self.make_box(contents=contents, finger_holes=finger_holes)

    # ------------------------------------------------------------------
    # Contents (compartments / inserts)
    # ------------------------------------------------------------------

    def _resolve_contents(self, contents: "Contents | None") -> list[InnerObject]:
        """Normalise *contents* into a flat ``list[InnerObject]``.

        *contents* may be ``None``, a plain ``list[InnerObject]``, or a
        ``callable(InnerSize) -> list[InnerObject]`` for content that needs to
        know the box interior size (the Pythonic replacement for the SCAD
        ``$inner_*`` special variables).
        """
        if contents is None:
            return []
        if callable(contents):
            inner = InnerSize(width=self.inner_width, length=self.inner_length, height=self.inner_height)
            resolved = contents(inner)
        else:
            resolved = contents
        return list(resolved) if resolved else []

    # ------------------------------------------------------------------
    # _finish_box -- shared body-assembly pipeline (called from subclass make_box)
    # ------------------------------------------------------------------

    def _finish_box(
        self,
        body: Bosl2Solid,
        contents: "Contents | None" = None,
        finger_holes: list[FingerHole] | None = None,
    ) -> Bosl2Solid:
        """Apply the inside mask, contents, finger holes, MMU and positioning to *body*.

        When *contents* or *finger_holes* are ``None``, the corresponding
        fields from the :class:`BoxSpec` (set at construction) are used.
        """
        if contents is None and self._spec.contents is not None:
            contents = self._spec.contents
        if finger_holes is None and self._spec.finger_holes is not None:
            finger_holes = self._spec.finger_holes
        self._contents = self._resolve_contents(contents)

        # Hollow the interior with the inside mask so an empty box is a usable
        # open box rather than a solid block.
        body = body - self.inside_mask()

        body = self._carve_contents(body)
        if finger_holes:
            body = self._apply_finger_holes(body, finger_holes)
        body = self._apply_mmu(body)
        body = self._apply_positioning(body)
        self._body = body
        return body

    def _placed_content(self, io: InnerObject) -> Bosl2Solid:
        """Resolve *io*'s value and translate it into the box interior frame."""
        piece = ResolveChild(io.value, self.inner_width, self.inner_length, self.inner_height)
        return piece.translate([self.wall_thickness, self.wall_thickness, self.floor_thickness])

    def _carve_contents(self, body: Bosl2Solid) -> Bosl2Solid:
        """Subtract every negative content, clipped to the inside mask so it
        cannot punch through the walls or floor."""
        result = body
        for io in self._contents:
            if io.type in (ObjectType.NEGATIVE, ObjectType.POSTIVE_NEGATIVE):
                # inside_mask() (a Bosl2Solid) must be the left operand: its __and__
                # unwraps the right side, whereas a raw native handle on the left
                # raises "invalid argument left to operator" for a Bosl2Solid RHS.
                result = result - (self.inside_mask() & self._placed_content(io))
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
        """Union coloured copies of positive contents back onto the body.

        ``POSTIVE`` contents are always emitted as solid (non-carved) copies;
        ``POSTIVE_NEGATIVE`` contents are additionally emitted only when building
        for multi-material (``MAKE_MMU == 1``).
        """
        result = body
        extra = None
        for io in self._contents:
            emit = io.type == ObjectType.POSTIVE or (io.type == ObjectType.POSTIVE_NEGATIVE and MAKE_MMU == 1)
            if not emit:
                continue
            piece = self._placed_content(io).color(io.color if io.color is not None else self.positive_colour)
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
        """Create a label solid from *label* using this Box's dimensions and colour.

        Converts the :class:`Label` data object into rendering options and calls
        :func:`~lids_base.MakeLidLabel`, positioning the result inside the box.
        """
        from lids_base import MakeLidLabel

        effective_colour = (
            self.material_colour
            if label.material_colour == default_material_colour
            else label.material_colour
        )
        options = MakeLabelOptions(
            text_scale=label.text_scale,
            text_length=label.text_length,
            angle=label.angle,
            label_colour=label.label_colour,
            label_background_colour=label.label_background_colour,
            short_length=label.short_length,
            label_diff=list(label.label_diff),
            border=label.border,
            offset=label.offset,
            radius=label.radius,
            font=label.font,
            full_height=label.full_height,
            finger_hole_size=label.finger_hole_size,
            material_colour=effective_colour,
            label_type=label.label_type,
            solid_background=label.solid_background,
        )

        calc_size = list(label.size) if label.size else [self.inner_width, self.inner_length]
        calc_pos = (
            list(label.position)
            if label.position
            else [self.wall_thickness / 2, self.wall_thickness / 2, 0]
        )

        piece = MakeLidLabel(
            size=calc_size,
            lid_thickness=self.lid_thickness,
            text_str=label.text,
            options=options,
        )
        if piece is not None:
            return piece.translate(calc_pos)
        return None

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
