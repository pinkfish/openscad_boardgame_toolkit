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
#    BoxBaseType -- the abstract base type that all box types inherit from -- plus
#    BoxSpec (the validated, immutable configuration), the BoxKit factory, and the
#    small value types (FingerHole, Label) the box pipeline consumes.
#
# FileSummary: Base box type for building boxes.
# FileGroup: Basics

from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields, replace
from enum import IntEnum
from typing import Any, Callable, Union

import pybosl2.shapes3d
import pybosl2.transforms
from pybosl2.shapes3d import Bosl2Solid

# Explicit imports (no `import *`): every name below is traceable to its source.
from base_bgtk import (
    BACK,
    BOT,
    BOTTOM,
    FRONT,
    LEFT,
    RIGHT,
    TOP,
    MAKE_MMU,
    InnerObject,
    InnerSize,
    ObjectType,
    ResolveChild,
    default_floor_thickness,
    default_lid_thickness,
    default_material_colour,
    default_positive_colour,
    default_wall_thickness,
    m_piece_wiggle_room,
)
from components import FingerHoleBase, FingerHoleWall
from labels import LabelOptions
from lids_base import Lid, internal_build_lid
from shape_type import ShapeObject

# Box contents are self-describing InnerObject entries (see base_bgtk.InnerObject /
# ObjectType). They may be given directly as a list, or as a callable(InnerSize) for
# content that needs to know the box interior size.
Contents = Union[list[InnerObject], Callable[[InnerSize], list[InnerObject]]]


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


def finger_hole_cutter(
    fh: FingerHole,
    *,
    name: str,
    width: float,
    length: float,
    height: float,
    wall_thickness: float,
    floor_thickness: float,
) -> Bosl2Solid:
    """Return the finger-hole cutout solid for *fh*, positioned in the box frame.

    Pure function of the finger-hole spec and the box's outer dimensions -- it does
    not touch a box instance, so the placement geometry can be tested on its own.
    *name* is only used for error messages.
    """
    r = fh.radius if fh.radius is not None else 14
    rr = fh.rounding_radius if fh.rounding_radius is not None else 3

    if fh.type == FingerHoleType.FLOOR:
        h = fh.height if fh.height is not None else 14
        hole = FingerHoleBase(radius=r, height=h, rounding_radius=rr, wall_thickness=wall_thickness)
        # Floor holes sit at the interior floor, offset from centre along a wall side.
        if fh.location == FingerHoleLocation.LEFT:
            pos = [0 - wall_thickness / 2, length / 2 + fh.offset, floor_thickness]
        elif fh.location == FingerHoleLocation.RIGHT:
            pos = [width + wall_thickness / 2, length / 2 + fh.offset, floor_thickness]
        elif fh.location == FingerHoleLocation.FRONT:
            pos = [width / 2 + fh.offset, 0 - wall_thickness / 2, floor_thickness]
        elif fh.location == FingerHoleLocation.BACK:
            pos = [width / 2 + fh.offset, length + wall_thickness / 2, floor_thickness]
        else:
            raise ValueError(f"{name}: unknown finger hole location: {fh.location}")
        return hole.translate(pos)

    # Wall type -- cut through the side wall at half height.
    d = fh.depth if fh.depth is not None else 6
    h = fh.height if fh.height is not None else height / 2
    if fh.location == FingerHoleLocation.LEFT:
        pos, orient_val = [0, length / 2 + fh.offset, height / 2], RIGHT
    elif fh.location == FingerHoleLocation.RIGHT:
        pos, orient_val = [width, length / 2 + fh.offset, height / 2], LEFT
    elif fh.location == FingerHoleLocation.FRONT:
        pos, orient_val = [width / 2 + fh.offset, 0, height / 2], BACK
    elif fh.location == FingerHoleLocation.BACK:
        pos, orient_val = [width / 2 + fh.offset, length, height / 2], FRONT
    else:
        raise ValueError(f"{name}: unknown finger hole location: {fh.location}")

    hole = FingerHoleWall(
        radius=r,
        height=h,
        depth_of_hole=d,
        rounding_radius=rr,
        rounding_edge=fh.rounding_edge,
        orient=orient_val,
    )
    return hole.translate(pos)


@dataclass
class Label:
    """Text label to place on a lid: the *text* plus its styling and placement.

    Styling lives in a single :class:`~labels.LabelOptions` (``options``) rather than
    being duplicated field-by-field here -- so there is one styling type in the
    codebase, not two that must be copied back and forth.

    Usage::

        Label("Frogs")
        Label("Snakes", options=MakeLabelOptions(font="Stencil Std:style=Bold",
                                                 label_type=LabelType.FRAMELESS))
    """

    text: str
    options: LabelOptions = field(default_factory=LabelOptions)
    position: list[float] | None = None
    size: list[float] | None = None
    # An image to place on the lid INSTEAD OF the text: a 2-D shape (e.g. shapes.coin2d(30)),
    # a callable(depth), or a solid. When set, `text` is ignored.
    shape: object = None


@dataclass(frozen=True)
class BoxSpec:
    """Complete, **immutable** specification for a box: dimensions, materials,
    contents, and lid.

    ``BoxSpec`` is a frozen dataclass and validates itself on construction (see
    :meth:`__post_init__`), so an impossible box (non-positive dimensions, walls that
    don't fit) fails loudly at the point of definition rather than as a confusing
    geometry error deep in the build.

    Pass a single ``BoxSpec`` to any :class:`BoxBaseType` subclass constructor
    (e.g. ``SlidingBox(spec)``).  Call :meth:`~BoxBaseType.make_box` and
    :meth:`~BoxBaseType.make_lid` with **no arguments** to generate both parts from
    this single shared object -- the box and lid are therefore guaranteed to have
    matching dimensions and thicknesses.

    Usage::

        from box_base import BoxSpec, FingerHole, FingerHoleLocation
        from sliding_box import SlidingBox

        spec = BoxSpec(
            size=[100, 60, 30],
            label="EarthCardBox",
            wall_thickness=3,
            lid_thickness=2,
            contents=lambda inner: [
                InnerObject(pybosl2.shapes3d.cuboid([inner.width, inner.length, inner.height]))
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
    anchor: list[float] | None = None   # None -> BOTTOM + FRONT + LEFT
    orient: list[float] | None = None   # None -> TOP

    # ---- Box-type-specific options -------------------------------------------
    # ``type_options`` is the generic, type-agnostic slot: each box type reads
    # whatever object it needs from it (SlidingBox reads MakeSlidingLidOptions(), a
    # future CapBox its own options, ...). The SAME spec can therefore be built by
    # any box type -- switch the type (e.g. via BoxKit) without touching this.
    type_options: Any = None
    # Alias kept working for the module-level helpers/examples that predate
    # ``type_options``: SlidingBox falls back to it when ``type_options`` is None.
    sliding_lid_options: Any = None

    # ---- Contents (inner compartments / inserts) -----------------------------
    contents: Contents | None = None
    finger_holes: list[FingerHole] | None = None
    # Force the interior hollow (open box) even for a box type that is otherwise solid
    # when empty -- how a no-lid box usually renders. Ignored when compartments carve
    # their own cavities.
    hollow: bool = False

    # ---- Lid configuration ---------------------------------------------------
    # Use ``lid_label`` for the common case (text + default shape pattern).
    # Use ``lid`` for full control (pass a pre-built :class:`~lids_base.Lid`).
    # ``lid`` takes precedence over ``lid_label`` when both are set.
    lid_label: str | None = None              # shorthand label text for the lid
    lid_shape: object = None                  # a SHAPE image on the lid instead of a text label
    lid: Lid | None = None                    # full Lid object (overrides lid_label/lid_shape)
    label_options: LabelOptions | None = None # styling for lid_label
    shape_options: ShapeObject | None = None  # lid pattern shape (the tiled background)

    def __post_init__(self) -> None:
        if not (isinstance(self.size, (list, tuple)) and len(self.size) == 3):
            raise ValueError(f"{self.label}: size must be [width, length, height], got {self.size!r}")
        w, l, h = self.size
        if min(w, l, h) <= 0:
            raise ValueError(f"{self.label}: every dimension must be > 0, got {self.size!r}")
        if self.wall_thickness <= 0 or self.floor_thickness <= 0 or self.lid_thickness <= 0:
            raise ValueError(
                f"{self.label}: wall/floor/lid thickness must be > 0, got "
                f"{self.wall_thickness}/{self.floor_thickness}/{self.lid_thickness}"
            )
        # The interior must actually exist. (Height vs floor+lid is intentionally NOT
        # checked here: some helpers build a lid-only spec whose height == lid_thickness.)
        if self.wall_thickness * 2 >= w or self.wall_thickness * 2 >= l:
            raise ValueError(
                f"{self.label}: walls (2 x {self.wall_thickness}) don't fit in "
                f"width {w} / length {l} -- interior would be non-positive"
            )


class BoxBaseType(ABC):
    """Abstract base type that **every** board game toolkit box type inherits from.

    ``BoxBaseType`` defines the common contract and machinery shared by all box
    types (SlidingBox, and future CapBox / SlipoverBox / ...): construction from a
    single :class:`BoxSpec`, the derived-dimension properties, the interior
    hollowing + content carving + finger-hole + MMU + positioning pipeline
    (:meth:`_finish_box`), and the lid-composition helpers.

    It is abstract at the right seam: :meth:`make_box` and :meth:`make_lid` are
    concrete template methods, and the ONE thing each box type must supply is
    :meth:`_build_box_body` (how its specific body is shaped). A type MAY also
    override :meth:`inside_mask`, :meth:`create_lid` and :meth:`_make_base_lid`.

    No geometry is built at construction time; call :meth:`make_box` /
    :meth:`make_lid` (both with **no arguments** when a spec is provided) to produce
    the two printable parts.

    Usage::

        spec = BoxSpec(size=[50, 100, 30], label="mybox", wall_thickness=3,
                       contents=lambda inner: [InnerObject(cavity)],
                       finger_holes=[FingerHole(location=FingerHoleLocation.LEFT)],
                       lid_label="Trains")
        box = SlidingBox(spec)
        box.make_box().show()
        box.make_lid().show()
    """

    def __init__(self, spec: BoxSpec) -> None:
        if not isinstance(spec, BoxSpec):
            raise TypeError(
                f"{type(self).__name__} expects a BoxSpec, got {type(spec).__name__}. "
                "Construct with BoxSpec(size=[w, l, h], label='name', ...)."
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
    # Dimensions (derived)
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

    def _effective_height(self) -> float:
        """Height of the actual body geometry. Subclasses whose body isn't the full
        outer height (e.g. a sliding box with a top lid layer) override this."""
        return self.height

    # ------------------------------------------------------------------
    # make_box -- concrete template; subclasses supply _build_box_body
    # ------------------------------------------------------------------

    def make_box(
        self,
        *,
        contents: Contents | None = None,
        finger_holes: list[FingerHole] | None = None,
    ) -> Bosl2Solid:
        """Build the box: this type's body (:meth:`_build_box_body`) run through the
        shared finishing pipeline (:meth:`_finish_box`).

        ``contents`` / ``finger_holes`` default to the values from the :class:`BoxSpec`
        given at construction when omitted.
        """
        return self._finish_box(self._build_box_body(), contents=contents, finger_holes=finger_holes)

    @abstractmethod
    def _build_box_body(self) -> Bosl2Solid:
        """Build the raw (solid, not yet hollowed) box body for this box type.

        The ONE method every concrete box type must implement -- it is the only part
        of box construction that actually differs between types. Everything after it
        (hollowing, contents, finger holes, MMU, positioning) is shared."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # _finish_box -- shared body-assembly pipeline (pure; no hidden state)
    # ------------------------------------------------------------------

    def _finish_box(
        self,
        body: Bosl2Solid,
        contents: Contents | None = None,
        finger_holes: list[FingerHole] | None = None,
    ) -> Bosl2Solid:
        """Hollow *body*, carve negative contents, cut finger holes, add MMU positive
        copies, and position. ``contents`` / ``finger_holes`` fall back to the spec."""
        if contents is None:
            contents = self._spec.contents
        if finger_holes is None:
            finger_holes = self._spec.finger_holes
        resolved = self._resolve_contents(contents)

        mask = self.inside_mask()          # build once and reuse
        has_cavities = any(io.type in (ObjectType.NEGATIVE, ObjectType.POSITIVE_NEGATIVE) for io in resolved)
        if self._should_hollow(has_cavities):
            # Open the whole interior (an empty tray, or an explicit hollow=True box).
            body = body - mask
        if has_cavities:
            # Compartments define the cavities: carve them (clipped to the interior)
            # out of the SOLID interior, so the material between and under them is
            # left behind as dividers and floors.
            body = self._carve_contents(body, resolved, mask)
        if finger_holes:
            body = self._apply_finger_holes(body, finger_holes)
        body = self._apply_mmu(body, resolved, MAKE_MMU)
        return self._apply_positioning(body)

    def inside_mask(self) -> Bosl2Solid:
        """The interior volume -- subtracted to hollow the box and used to clip
        negative contents so they can't punch through walls or floor."""
        return pybosl2.shapes3d.cuboid(
            [self.inner_width, self.inner_length, self.inner_height],
            anchor=BOTTOM + FRONT + LEFT,
        ).translate([self.wall_thickness, self.wall_thickness, self.floor_thickness])

    def _hollow_when_empty(self) -> bool:
        """Whether a box with NO negative contents is hollowed to an open box. True for
        lidded containers (an empty tray is open); a box type whose empty form is a
        solid spacer (e.g. NoLidBox) overrides this to False and opts in via
        ``BoxSpec.hollow``."""
        return True

    def _should_hollow(self, has_cavities: bool) -> bool:
        """Decide whether to subtract the full interior. ``BoxSpec.hollow=True`` always
        hollows; otherwise a box with compartments is left solid (they carve the
        cavities) and an empty box follows :meth:`_hollow_when_empty`."""
        if self._spec.hollow:
            return True
        if has_cavities:
            return False
        return self._hollow_when_empty()

    # ------------------------------------------------------------------
    # Contents (compartments / inserts)
    # ------------------------------------------------------------------

    def _resolve_contents(self, contents: Contents | None) -> list[InnerObject]:
        """Normalise *contents* into a flat ``list[InnerObject]``.

        *contents* may be ``None``, a plain ``list[InnerObject]``, or a
        ``callable(InnerSize) -> list[InnerObject]`` for content that needs to know the
        box interior size (the Pythonic replacement for SCAD's ``$inner_*`` vars)."""
        if contents is None:
            return []
        if callable(contents):
            inner = InnerSize(width=self.inner_width, length=self.inner_length, height=self.inner_height)
            resolved = contents(inner)
        else:
            resolved = contents
        return list(resolved) if resolved else []

    def _placed_content(self, io: InnerObject) -> Bosl2Solid:
        """Resolve *io*'s value and translate it into the box interior frame."""
        piece = ResolveChild(io.value, self.inner_width, self.inner_length, self.inner_height)
        return piece.translate([self.wall_thickness, self.wall_thickness, self.floor_thickness])

    def _carve_contents(self, body: Bosl2Solid, contents: list[InnerObject], mask: Bosl2Solid) -> Bosl2Solid:
        """Subtract every negative content, clipped to *mask* so it cannot punch
        through the walls or floor."""
        result = body
        for io in contents:
            if io.type not in (ObjectType.NEGATIVE, ObjectType.POSITIVE_NEGATIVE):
                continue
            piece = self._placed_content(io)
            if getattr(io, "clip", True):
                # mask (a Bosl2Solid) must be the LEFT operand: its __and__ unwraps the
                # right side, whereas a raw native handle on the left rejects a
                # Bosl2Solid RHS ("invalid argument left to operator").
                result = result - (mask & piece)
            else:
                # Breaching cut (e.g. a card finger hole): subtract raw so it can go
                # through the floor / walls.
                result = result - piece
        return result

    def _apply_finger_holes(self, body: Bosl2Solid, finger_holes: list[FingerHole]) -> Bosl2Solid:
        result = body
        for fh in finger_holes:
            result = result - finger_hole_cutter(
                fh,
                name=self.label,
                width=self.width,
                length=self.length,
                height=self.height,
                wall_thickness=self.wall_thickness,
                floor_thickness=self.floor_thickness,
            )
        return result

    def _apply_mmu(self, body: Bosl2Solid, contents: list[InnerObject], make_mmu: int) -> Bosl2Solid:
        """Union coloured copies of positive contents back onto *body*.

        ``POSITIVE`` contents are always emitted; ``POSITIVE_NEGATIVE`` contents are
        emitted only when building for multi-material (``make_mmu == 1``)."""
        extra = None
        for io in contents:
            emit = io.type == ObjectType.POSITIVE or (io.type == ObjectType.POSITIVE_NEGATIVE and make_mmu == 1)
            if not emit:
                continue
            piece = self._placed_content(io).color(io.color if io.color is not None else self.positive_colour)
            extra = piece if extra is None else extra | piece
        return body if extra is None else body | extra

    # ------------------------------------------------------------------
    # Positioning
    # ------------------------------------------------------------------

    def _apply_positioning(self, body: Bosl2Solid) -> Bosl2Solid:
        # Two different heights on purpose (verified correct for single- AND two-layer):
        # the pre-translate recentres in the DECLARED outer-height frame (self.height,
        # the box's nominal size), while reorient sizes the anchor box by the ACTUAL body
        # height (_effective_height(), which a two-layer sliding lid makes < self.height).
        tmat = pybosl2.transforms.reorient(
            anchor=self.anchor,
            spin=self.spin,
            orient=self.orient,
            size=[self.width, self.length, self._effective_height()],
        )
        return body.translate([-self.width / 2, -self.length / 2, -self.height / 2]).multmatrix(tmat)

    # ------------------------------------------------------------------
    # make_lid -- concrete template; subclasses supply _make_base_lid / _lid_adjustment
    # ------------------------------------------------------------------

    def make_lid(self, lid: Lid | None = None) -> Bosl2Solid:
        """Make the lid for this box -- the second of the two top-level methods.

        With no argument (and a :class:`BoxSpec` given at construction) the lid is
        built from :attr:`BoxSpec.lid` or :attr:`BoxSpec.lid_label` /
        :attr:`BoxSpec.shape_options`. Pass an explicit :class:`~lids_base.Lid` to
        override the spec."""
        if lid is None:
            lid = self._resolve_lid_from_spec()
        return self.create_lid(lid)

    def _resolve_lid_from_spec(self) -> Lid | None:
        """Build a :class:`~lids_base.Lid` from the :class:`BoxSpec`, or ``None`` when
        neither :attr:`BoxSpec.lid` nor :attr:`BoxSpec.lid_label` is set."""
        spec = self._spec
        if spec.lid is not None:
            return spec.lid
        if spec.lid_label is not None or spec.lid_shape is not None:
            options = spec.label_options if spec.label_options is not None else LabelOptions()
            return Lid(
                lid_thickness=self.lid_thickness,
                label=Label(spec.lid_label or "", options=options, shape=spec.lid_shape),
                shape_options=spec.shape_options,
                material_colour=self.material_colour,
            )
        return None

    def create_lid(self, lid: Lid | None = None) -> Bosl2Solid:
        """Create the lid: base body (:meth:`_make_base_lid`) plus the lid's shape
        pattern / label / fingernail overlay, stacked by
        :func:`~lids_base.internal_build_lid`.

        The passed *lid* is never mutated -- a copy is filled in with this box's
        defaults so the same :class:`~lids_base.Lid` can be reused across boxes."""
        l = copy.copy(lid) if lid is not None else Lid(lid_thickness=self.lid_thickness)
        if not l.lid_thickness:
            l.lid_thickness = self.lid_thickness
        if l.size is None:
            l.size = [self.inner_width, self.inner_length]
        if l.fingernail is not None and l.fingernail.enabled:
            l.fingernail = replace(l.fingernail)   # don't mutate the caller's Fingernail
            if l.fingernail.width is None:
                l.fingernail.width = self.inner_width
                l.fingernail.length = self.inner_length

        children = [self._make_base_lid(l.lid_rounding)] + self._lid_overlay(l)
        stack = internal_build_lid(
            lid_thickness=l.lid_thickness,
            children=children,
            size_spacing=self.size_spacing,
        )
        return self._lid_adjustment(stack)

    def _make_base_lid(self, lid_rounding: float | None = None) -> Bosl2Solid:
        """Build the raw lid body. Subclasses override for box-specific geometry."""
        return pybosl2.shapes3d.cuboid(
            [self.inner_width, self.inner_length, self.lid_thickness],
            anchor=BOTTOM + FRONT + LEFT,
        ).color(self.material_colour)

    def _lid_overlay(self, lid: Lid) -> list:
        """The overlay children (shape mesh, label, fingernail, extras) for *lid*."""
        return lid.overlay(label_builder=self.make_label)

    def _lid_adjustment(self, stack: Bosl2Solid) -> Bosl2Solid:
        """Post-process the assembled lid stack. Subclasses MAY override."""
        return stack

    # ------------------------------------------------------------------
    # Label creation
    # ------------------------------------------------------------------

    def make_label(self, label: Label) -> Bosl2Solid | None:
        """Build a label solid from *label* using this box's dimensions and colour.

        Uses the label's own :class:`~labels.LabelOptions` directly (only the material
        colour is defaulted to the box's), then positions it inside the box."""
        from lids_base import MakeLidLabel

        opts = label.options
        effective_colour = (
            self.material_colour if opts.material_colour == default_material_colour else opts.material_colour
        )
        options = replace(opts, material_colour=effective_colour)

        calc_size = list(label.size) if label.size else [self.inner_width, self.inner_length]

        # A SHAPE image instead of text: extrude it to the lid thickness, colour it the LABEL
        # colour (a contrasting second material, like the text label -- NOT the body colour),
        # and centre it on the lid (or the caller's position). The caller pre-sizes the shape.
        if label.shape is not None:
            from components import _extrude_image

            pos = list(label.position) if label.position else [self.inner_width / 2, self.inner_length / 2, 0]
            return _extrude_image(label.shape, self.lid_thickness).color(opts.label_colour).translate(pos)

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
        return piece.translate(calc_pos) if piece is not None else None


class BoxKit:
    """Binds ONE box type plus a set of shared spec defaults, so a whole file of
    boxes is configured once and can be switched between box types in a single place.

    A ``BoxKit`` solves two problems at once:

    * **Configure the basic parts once.** Give the kit the settings every box in
      your project shares (wall/floor/lid thickness, material colour, label styling,
      lid options, ...). Each individual box then only specifies what is unique to it
      (size, label, contents, ...).
    * **Switch the whole system between box types in one edit.** The box *type* lives
      only in the kit (``BoxKit(SlidingBox, ...)``). Change that one class name to
      rebuild every box as a different type -- the per-box specs never mention the
      type, so nothing else has to change.

    Usage::

        from box_base import BoxKit
        from sliding_box import SlidingBox

        kit = BoxKit(SlidingBox, wall_thickness=2, lid_thickness=3, label_options=BLUE)

        seals = kit.box(size=[tw, tl, sh], label="Seals",
                        contents=lambda inner: [InnerObject(RoundedBoxAllSides(...))],
                        lid_label="Seals")
        seals.make_box().show()
        seals.make_lid().show()

        # Switch the ENTIRE project to cap boxes -> change one word:
        #     kit = BoxKit(CapBox, wall_thickness=2, lid_thickness=3, label_options=BLUE)

    Kit defaults and per-call overrides are merged per box (the call wins). Unknown
    keys are rejected up front (with the offending name) rather than surfacing as a
    cryptic ``BoxSpec`` error later.
    """

    _SPEC_FIELDS = frozenset(f.name for f in fields(BoxSpec))

    def __init__(self, box_class: "type[BoxBaseType]", **defaults: Any) -> None:
        self._reject_unknown(defaults, "BoxKit default")
        self.box_class = box_class
        self.defaults = defaults

    @classmethod
    def _reject_unknown(cls, kwargs: dict, what: str) -> None:
        bad = set(kwargs) - cls._SPEC_FIELDS
        if bad:
            raise TypeError(f"{what}(s) are not BoxSpec fields: {sorted(bad)}")

    def spec(self, **overrides: Any) -> BoxSpec:
        """Build a :class:`BoxSpec` from the kit's shared defaults + per-box overrides
        (the override wins for any field set in both)."""
        self._reject_unknown(overrides, "BoxKit override")
        return BoxSpec(**{**self.defaults, **overrides})

    def box(self, **overrides: Any) -> "BoxBaseType":
        """Construct a box object (of this kit's type) from the merged spec. Call
        :meth:`BoxBaseType.make_box` / :meth:`BoxBaseType.make_lid` on it to build the
        two matching parts."""
        return self.box_class(self.spec(**overrides))

    def with_type(self, box_class: "type[BoxBaseType]") -> "BoxKit":
        """Return a copy of this kit that builds *box_class* instead, keeping all
        shared defaults -- the programmatic form of switching the box type."""
        return BoxKit(box_class, **self.defaults)
