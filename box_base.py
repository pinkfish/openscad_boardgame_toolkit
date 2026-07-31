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
#    BoxSpec (the validated, immutable configuration), Interior (the interior frame),
#    LidPlate (the one lid contract), BoxTypeOptions (the typed per-type options base),
#    the BoxKit factory, and the small value types (FingerHole, Label) the box pipeline
#    consumes.
#
# FileSummary: Base box type for building boxes.
# FileGroup: Basics

from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields, replace
from enum import IntEnum
from typing import Any, Callable, ClassVar, Sequence, Union

import pybosl2.shapes3d
import pybosl2.transforms
from pybosl2.shapes3d import Bosl2Solid

# Explicit imports (no `import *`): every name below is traceable to its source.
from base_bgtk import (
    BACK,
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


# Finger-hole geometry defaults, in mm. Named (rather than inline literals in the cutter)
# because these are the numbers that decide whether a human finger actually fits.
default_finger_hole_radius = 14.0        # radius of the scoop / channel
default_finger_hole_rounding = 3.0       # roundover where the scoop meets the wall
default_finger_hole_depth = 6.0          # how far a WALL hole cuts into the wall
default_floor_finger_hole_height = 14.0  # height of a FLOOR hole above the interior floor


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
    radius: float = default_finger_hole_radius
    rounding_radius: float = default_finger_hole_rounding
    depth: float = default_finger_hole_depth
    rounding_edge: float = 0.0
    # None -> derived from the box: half the box height (WALL) /
    # default_floor_finger_hole_height (FLOOR).
    height: float | None = None


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
    if fh.type == FingerHoleType.FLOOR:
        h = fh.height if fh.height is not None else default_floor_finger_hole_height
        hole = FingerHoleBase(
            radius=fh.radius, height=h, rounding_radius=fh.rounding_radius, wall_thickness=wall_thickness
        )
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
        radius=fh.radius,
        height=h,
        depth_of_hole=fh.depth,
        rounding_radius=fh.rounding_radius,
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

    ``position`` / ``size`` default to the lid plate the label is placed on (see
    :class:`LidPlate`), so a label is centred on whatever face the box type decorates
    without every box type having to work the placement out for itself.

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


class BoxTypeOptions:
    """Marker base for every box type's options object.

    Each box type declares the exact options class it accepts
    (:attr:`BoxBaseType.options_class`) and :class:`BoxBaseType` validates
    ``BoxSpec.type_options`` against it at CONSTRUCTION time. Passing a sliding box's
    options to a cap box is therefore an immediate, named ``TypeError`` -- not (as it
    once was) either a silent fall-back to defaults or an ``AttributeError`` thrown
    from deep inside the geometry.
    """


@dataclass(frozen=True)
class Interior:
    """The usable interior of a box: where it starts, how big it is, and (for a
    non-rectangular box) the outline it is bounded by.

    ONE object defines the interior frame, so the three things that must agree --
    the reported ``inner_width``/``inner_length``/``inner_height``, where contents are
    placed, and the volume they are clipped to -- cannot drift apart. A box type with
    an unusual interior overrides :meth:`BoxBaseType._compute_interior` (and, only when
    the clip volume is not the box of this frame, :meth:`BoxBaseType.interior_mask`).

    Attributes:
        origin: box-frame coordinates of the interior's BOTTOM+FRONT+LEFT corner
        size:   ``[width, length, height]`` of the usable interior
        region: optional polygon outline of the interior in the LOCAL frame
                (``0..width x 0..length``); ``None`` -> the full rectangle
    """

    origin: tuple[float, float, float]
    size: tuple[float, float, float]
    region: Any = None

    @property
    def width(self) -> float:
        return self.size[0]

    @property
    def length(self) -> float:
        return self.size[1]

    @property
    def height(self) -> float:
        return self.size[2]


@dataclass
class LidPlate:
    """What a box type hands the lid pipeline: the flat face the decoration goes on,
    plus whatever else the lid is made of.

    EVERY lid in the toolkit is described by this one contract, so there is a single
    lid pipeline (:meth:`BoxBaseType.make_lid`) rather than a different one per box
    type. A box type implements :meth:`BoxBaseType._lid_plate` and nothing else:

    * ``plate`` is a flat slab occupying ``z = 0 .. thickness`` -- overlays (pattern
      mesh, label, fingernail) are always assembled onto it AT THE ORIGIN, because
      :func:`~lids_base.internal_build_lid` flattens overlays to ``z = 0``.
    * ``shell`` is everything else (cap walls, a sleeve, hinge knuckles, tabs), already
      in its final position.
    * ``offset`` is where the decorated plate is moved to before being joined to the
      shell -- e.g. ``[0, 0, cap_height]`` for a cap lid's top face.

    Attributes:
        plate:          the flat slab, at ``z = 0 .. thickness``
        size:           ``[width, length]`` footprint the overlays are fitted to
        thickness:      slab thickness
        origin:         ``[x, y]`` of the slab footprint's minimum corner, in plate
                        coordinates (non-zero for a polygon lid centred on the origin,
                        or a sliding lid overhanging its box) -- the label and
                        fingernail are placed relative to it
        offset:         translation applied to the decorated plate
        shell:          the rest of the lid, or ``None``
        path:           polygon outline of the plate for the pattern mesh; ``None``
                        -> the ``size`` rectangle
        extra_overlays: structural pieces that must go through the overlay stack with
                        the decoration (e.g. a card box's latch supports)
        cutouts:        solids subtracted from the finished lid (a hinge pin hole, a
                        latch slot) -- applied after the plate and shell are joined
    """

    plate: Bosl2Solid
    size: Sequence[float]
    thickness: float
    origin: Sequence[float] = (0.0, 0.0)
    offset: Sequence[float] = (0.0, 0.0, 0.0)
    shell: Bosl2Solid | None = None
    path: Any = None
    extra_overlays: Sequence[Any] = ()
    cutouts: Sequence[Any] = ()


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

    # ---- Positioning (applied to the finished box by _apply_positioning) ------
    spin: float = 0
    anchor: list[float] | None = None   # None -> BOTTOM + FRONT + LEFT
    orient: list[float] | None = None   # None -> TOP

    # ---- Box-type-specific options -------------------------------------------
    # The options object for the box type this spec is built with -- a
    # :class:`BoxTypeOptions` subclass named by that type's ``options_class`` (e.g.
    # CapBoxOptions for CapBox). It is TYPE-CHECKED when the box is constructed, so a
    # spec carrying one type's options cannot be quietly built as another type.
    type_options: BoxTypeOptions | None = None

    # ---- Contents (inner compartments / inserts) -----------------------------
    contents: Contents | None = None
    finger_holes: list[FingerHole] | None = None
    # Force the interior hollow (an open box). This wins over everything else: a box
    # with compartments AND hollow=True is hollowed first, which dissolves the material
    # the compartments would have left as dividers. Leave it False when using
    # compartments; it exists for box types that are a solid spacer when empty
    # (NoLidBox / PathBox), which is what a no-lid box usually wants.
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

    ``BoxBaseType`` owns the whole box pipeline; a box type supplies geometry and
    nothing else. There are exactly THREE things a subclass can implement:

    * :meth:`_build_box_body` -- the raw body (required).
    * :meth:`_lid_plate` -- the lid's flat decorated face + shell, as a
      :class:`LidPlate` (only if the lid isn't a plain slab).
    * :meth:`_compute_interior` / :meth:`interior_mask` -- the interior frame (only if
      it isn't ``wall_thickness`` in from the outer box).

    Everything else -- resolving contents, hollowing, carving, MMU colour copies,
    finger holes, positioning, and the entire lid decoration stack -- happens once,
    here, for every type. A box type that builds its body through legacy geometry that
    already hollows itself or already embeds contents says so with the
    :attr:`body_hollows_itself` / :attr:`body_carves_contents` class flags, instead of
    overriding :meth:`make_box` and silently dropping the rest of the pipeline.

    Usage::

        spec = BoxSpec(size=[50, 100, 30], label="mybox", wall_thickness=3,
                       contents=lambda inner: [InnerObject(cavity)],
                       finger_holes=[FingerHole(location=FingerHoleLocation.LEFT)],
                       lid_label="Trains")
        box = SlidingBox(spec)
        box.make_box().show()
        box.make_lid().show()
    """

    #: The :class:`BoxTypeOptions` subclass this box type accepts in
    #: ``BoxSpec.type_options``; ``None`` -> the type takes no options.
    options_class: ClassVar[type[BoxTypeOptions] | None] = None

    #: False for a box that is a single piece or has no lid at all; :meth:`make_lid`
    #: then raises with a uniform message instead of each type inventing its own.
    has_lid: ClassVar[bool] = True

    #: True when :meth:`_build_box_body` already opens the interior itself (legacy
    #: geometry that hollows internally), so the shared stage must not subtract again.
    body_hollows_itself: ClassVar[bool] = False

    #: True when :meth:`_build_box_body` already consumes ``contents`` itself (geometry
    #: with its own content slots, e.g. a hinged box's four compartments), so the shared
    #: carve + MMU stage is skipped. Finger holes and positioning still apply.
    body_carves_contents: ClassVar[bool] = False

    def __init__(self, spec: BoxSpec) -> None:
        if not isinstance(spec, BoxSpec):
            raise TypeError(
                f"{type(self).__name__} expects a BoxSpec, got {type(spec).__name__}. "
                "Construct with BoxSpec(size=[w, l, h], label='name', ...)."
            )
        self._spec = spec
        self.options = self._resolve_options(spec.type_options)
        self.positive_colour = default_positive_colour
        self.size_spacing = m_piece_wiggle_room

    @classmethod
    def _resolve_options(cls, given: Any) -> Any:
        """Validate ``BoxSpec.type_options`` against this type's :attr:`options_class`.

        Wrong type in, immediate ``TypeError`` naming both classes -- the one place the
        "which options does this box take?" question is answered."""
        if cls.options_class is None:
            if given is not None:
                raise TypeError(
                    f"{cls.__name__} takes no type_options, got {type(given).__name__}. "
                    "Remove BoxSpec(type_options=...)."
                )
            return None
        if given is None:
            try:
                return cls.options_class()
            except TypeError as exc:   # options with required fields (e.g. a path)
                raise TypeError(
                    f"{cls.__name__} requires BoxSpec(type_options="
                    f"{cls.options_class.__name__}(...)): {exc}"
                ) from exc
        if not isinstance(given, cls.options_class):
            raise TypeError(
                f"{cls.__name__} expects BoxSpec(type_options={cls.options_class.__name__}(...)), "
                f"got {type(given).__name__}."
            )
        return given

    # ------------------------------------------------------------------
    # Spec-backed values (read-only: the BoxSpec stays the single source of truth)
    # ------------------------------------------------------------------

    @property
    def spec(self) -> BoxSpec:
        return self._spec

    @property
    def label(self) -> str:
        return self._spec.label

    @property
    def wall_thickness(self) -> float:
        return self._spec.wall_thickness

    @property
    def floor_thickness(self) -> float:
        return self._spec.floor_thickness

    @property
    def lid_thickness(self) -> float:
        return self._spec.lid_thickness

    @property
    def material_colour(self) -> str:
        return self._spec.material_colour

    @property
    def anchor(self) -> list[float]:
        return self._spec.anchor if self._spec.anchor is not None else BOTTOM + FRONT + LEFT

    @property
    def orient(self) -> list[float]:
        return self._spec.orient if self._spec.orient is not None else TOP

    @property
    def spin(self) -> float:
        return self._spec.spin

    # ------------------------------------------------------------------
    # Dimensions (derived)
    # ------------------------------------------------------------------

    @property
    def width(self) -> float:
        return self._spec.size[0]

    @property
    def length(self) -> float:
        return self._spec.size[1]

    @property
    def height(self) -> float:
        return self._spec.size[2]

    def interior(self) -> Interior:
        """This box's :class:`Interior` frame (computed once, then cached)."""
        cached = self.__dict__.get("_interior")
        if cached is None:
            cached = self.__dict__["_interior"] = self._compute_interior()
        return cached

    def _compute_interior(self) -> Interior:
        """The interior frame: a wall in from each side, floor to lid.

        The ONE method a box type overrides to describe its interior."""
        wt = self.wall_thickness
        return Interior(
            origin=(wt, wt, self.floor_thickness),
            size=(
                self.width - wt * 2,
                self.length - wt * 2,
                self.height - self.lid_thickness - self.floor_thickness,
            ),
        )

    @property
    def inner_width(self) -> float:
        return self.interior().width

    @property
    def inner_length(self) -> float:
        return self.interior().length

    @property
    def inner_height(self) -> float:
        return self.interior().height

    def _effective_height(self) -> float:
        """Height of the actual body geometry. Subclasses whose body isn't the full
        outer height (e.g. a sliding box with a top lid layer) override this."""
        return self.height

    # ------------------------------------------------------------------
    # make_box -- the ONE box pipeline
    # ------------------------------------------------------------------

    def make_box(
        self,
        *,
        contents: Contents | None = None,
        finger_holes: list[FingerHole] | None = None,
    ) -> Bosl2Solid:
        """Build the box: this type's body (:meth:`_build_box_body`) hollowed, carved,
        MMU-coloured, finger-holed and positioned.

        ``contents`` / ``finger_holes`` default to the values from the :class:`BoxSpec`
        given at construction when omitted. Every stage runs for every box type, so
        ``BoxSpec.anchor`` / ``orient`` / ``spin`` / ``finger_holes`` mean the same
        thing whichever type built the geometry.
        """
        resolved = self._resolve_contents(self._spec.contents if contents is None else contents)
        holes = self._spec.finger_holes if finger_holes is None else finger_holes

        body = self._build_box_body(resolved)
        if not self.body_carves_contents:
            body = self._hollow_and_carve(body, resolved)
            body = self._apply_mmu(body, resolved, MAKE_MMU)
        if holes:
            body = self._apply_finger_holes(body, holes)
        return self._apply_positioning(body)

    @abstractmethod
    def _build_box_body(self, contents: list[InnerObject]) -> Bosl2Solid:
        """Build this box type's body.

        *contents* is the resolved content list, passed so a type whose geometry embeds
        its contents itself (:attr:`body_carves_contents`) or that must decide its own
        hollowing (:attr:`body_hollows_itself`, via :meth:`should_hollow`) can use it.
        Types that leave contents to the shared pipeline -- most of them -- ignore it."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Interior: hollowing and content carving
    # ------------------------------------------------------------------

    def interior_mask(self) -> Bosl2Solid:
        """The interior volume -- subtracted to hollow the box, and used to clip negative
        contents so they can't punch through walls or floor.

        Defaults to the box of the :class:`Interior` frame; override only when the clip
        volume is a different shape (a polygon box's outline prism)."""
        interior = self.interior()
        return pybosl2.shapes3d.cuboid(
            list(interior.size), anchor=BOTTOM + FRONT + LEFT
        ).translate(list(interior.origin))

    def _hollow_when_empty(self) -> bool:
        """Whether a box with NO negative contents is hollowed to an open box. True for
        lidded containers (an empty tray is open); a box type whose empty form is a
        solid spacer (e.g. NoLidBox) overrides this to False and opts in via
        ``BoxSpec.hollow``."""
        return True

    def should_hollow(self, contents: list[InnerObject]) -> bool:
        """Whether the full interior is subtracted. ``BoxSpec.hollow=True`` always
        hollows (see the field docs -- it dissolves compartment dividers too); otherwise
        a box with compartments is left solid (they carve their own cavities) and an
        empty box follows :meth:`_hollow_when_empty`."""
        if self._spec.hollow:
            return True
        if self.has_cavities(contents):
            return False
        return self._hollow_when_empty()

    @staticmethod
    def has_cavities(contents: list[InnerObject]) -> bool:
        """True when *contents* carve cavities of their own (so the interior is left solid)."""
        return any(io.type in (ObjectType.NEGATIVE, ObjectType.POSITIVE_NEGATIVE) for io in contents)

    def _hollow_and_carve(self, body: Bosl2Solid, contents: list[InnerObject]) -> Bosl2Solid:
        """Open the interior and/or carve the negative contents into it."""
        hollow = (not self.body_hollows_itself) and self.should_hollow(contents)
        cavities = self.has_cavities(contents)
        if not hollow and not cavities:
            return body
        mask = self.interior_mask()          # build once and reuse
        if hollow:
            # Open the whole interior (an empty tray, or an explicit hollow=True box).
            body = body - mask
        if cavities:
            # Compartments define the cavities: carve them (clipped to the interior)
            # out of the SOLID interior, so the material between and under them is
            # left behind as dividers and floors.
            body = self._carve_contents(body, contents, mask)
        return body

    # ------------------------------------------------------------------
    # Contents (compartments / inserts)
    # ------------------------------------------------------------------

    def _resolve_contents(self, contents: Contents | None) -> list[InnerObject]:
        """Normalise *contents* into a flat ``list[InnerObject]``.

        *contents* may be ``None``, a plain ``list[InnerObject]``, or a
        ``callable(InnerSize) -> list[InnerObject]`` for content that needs to know the
        box interior size (the Pythonic replacement for SCAD's ``$inner_*`` vars). The
        ``InnerSize`` carries the interior's ``region`` outline, so a compartment layout
        in a non-rectangular box can drop cells that fall outside it."""
        if contents is None:
            return []
        if callable(contents):
            interior = self.interior()
            resolved = contents(
                InnerSize(
                    width=interior.width,
                    length=interior.length,
                    height=interior.height,
                    region=interior.region,
                )
            )
        else:
            resolved = contents
        return list(resolved) if resolved else []

    def _placed_content(self, io: InnerObject) -> Bosl2Solid:
        """Resolve *io*'s value and translate it into the box interior frame."""
        interior = self.interior()
        piece = ResolveChild(io.value, interior.width, interior.length, interior.height)
        return piece.translate(list(interior.origin))

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
        # Two different heights on purpose (see tests/test_box_geometry.py, which pins
        # this for single- AND two-layer boxes): the pre-translate recentres in the
        # DECLARED outer-height frame (self.height, the box's nominal size), while
        # reorient sizes the anchor box by the ACTUAL body height (_effective_height(),
        # which a two-layer sliding lid makes < self.height). With the default
        # anchor/orient/spin the pair composes to the identity.
        tmat = pybosl2.transforms.reorient(
            anchor=self.anchor,
            spin=self.spin,
            orient=self.orient,
            size=[self.width, self.length, self._effective_height()],
        )
        return body.translate([-self.width / 2, -self.length / 2, -self.height / 2]).multmatrix(tmat)

    # ------------------------------------------------------------------
    # make_lid -- the ONE lid pipeline
    # ------------------------------------------------------------------

    def make_lid(self, lid: Lid | None = None) -> Bosl2Solid:
        """Make the lid for this box -- the second of the two top-level methods.

        With no argument (and a :class:`BoxSpec` given at construction) the lid is built
        from :attr:`BoxSpec.lid`, or from :attr:`BoxSpec.lid_label` /
        :attr:`BoxSpec.lid_shape` / :attr:`BoxSpec.shape_options`. Pass an explicit
        :class:`~lids_base.Lid` to override the spec.

        The pipeline is the same for every box type: the type's :class:`LidPlate` says
        which flat face is decorated and what else the lid is made of; the decoration
        (pattern mesh, label, fingernail, extras) is stacked onto that face by
        :func:`~lids_base.internal_build_lid`; the result is placed and joined to the
        shell, then handed to :meth:`_lid_adjustment` for print orientation."""
        if not self.has_lid:
            raise NotImplementedError(
                f"{self.label}: a {type(self).__name__} has no separate lid "
                "(it is a single piece, or has no lid at all)"
            )
        resolved = self._resolve_lid(lid)
        plate = self._lid_plate(resolved)
        return self._lid_adjustment(self._assemble_lid(plate, resolved))

    def _resolve_lid(self, lid: Lid | None) -> Lid:
        """The :class:`~lids_base.Lid` to build: the caller's, else the spec's, else the
        spec's label/shape shorthand, else a plain undecorated lid.

        Always returns a COPY with this box's defaults filled in, so a ``Lid`` can be
        shared between boxes without being mutated."""
        spec = self._spec
        if lid is None:
            lid = spec.lid
        if lid is None and (spec.lid_label is not None or spec.lid_shape is not None
                            or spec.shape_options is not None):
            lid = Lid(
                lid_thickness=self.lid_thickness,
                label=(
                    Label(spec.lid_label or "", options=spec.label_options or LabelOptions(),
                          shape=spec.lid_shape)
                    if (spec.lid_label is not None or spec.lid_shape is not None)
                    else None
                ),
                shape_options=spec.shape_options,
                material_colour=self.material_colour,
            )
        if lid is None:
            return Lid(lid_thickness=self.lid_thickness, material_colour=self.material_colour)
        resolved = copy.copy(lid)
        if not resolved.lid_thickness:
            resolved.lid_thickness = self.lid_thickness
        return resolved

    def _lid_plate(self, lid: Lid) -> LidPlate:
        """The lid's decorated face (and any shell around it) -- the ONE lid hook.

        Defaults to a plain flat slab covering the interior footprint. A box type whose
        lid is a cap, a sleeve, a grooved slider or a polygon returns a
        :class:`LidPlate` describing it; it never assembles the decoration itself."""
        interior = self.interior()
        plate = pybosl2.shapes3d.cuboid(
            [interior.width, interior.length, lid.lid_thickness],
            anchor=BOTTOM + FRONT + LEFT,
        ).color(self.material_colour)
        return LidPlate(plate=plate, size=[interior.width, interior.length], thickness=lid.lid_thickness)

    def _assemble_lid(self, plate: LidPlate, lid: Lid) -> Bosl2Solid:
        """Stack the lid's decoration onto *plate* and join it to the shell.

        The decoration is fitted to the PLATE's footprint (its ``size``/``path``/
        ``origin``), which is what stops a label drifting off a lid whose plate isn't
        the box's interior rectangle."""
        lid.size = list(plate.size)
        lid.path = plate.path
        self._fill_fingernail_defaults(lid, plate)

        overlays = list(lid.overlay(label_builder=lambda label: self.make_label(label, plate)))
        overlays.extend(plate.extra_overlays)

        decorated = plate.plate
        if overlays:
            decorated = internal_build_lid(
                lid_thickness=plate.thickness,
                children=[plate.plate] + overlays,
                size_spacing=self.size_spacing,
            )
        if any(plate.offset):
            decorated = decorated.translate(list(plate.offset))
        body = decorated if plate.shell is None else (plate.shell | decorated)
        for cut in plate.cutouts:
            body = body - cut
        return body.color(self.material_colour)

    def _fill_fingernail_defaults(self, lid: Lid, plate: LidPlate) -> None:
        """Size/position an enabled fingernail scoop from the plate footprint (never
        mutating the caller's :class:`~lids_base.Fingernail`)."""
        fn = lid.fingernail
        if fn is None or not fn.enabled:
            return
        lid.fingernail = fn = replace(fn)
        ox, oy = plate.origin[0], plate.origin[1]
        pw, pl = plate.size[0], plate.size[1]
        if fn.width is None:
            fn.width = pw
        if fn.length is None:
            fn.length = pl
        if fn.x_offset is None:
            fn.x_offset = ox + pw / 2
        if fn.y_offset is None:
            fn.y_offset = oy + pl - 3

    def _lid_adjustment(self, stack: Bosl2Solid) -> Bosl2Solid:
        """Post-process the assembled lid -- flip it for printing, cut a hinge pin hole.
        Subclasses MAY override."""
        return stack

    # ------------------------------------------------------------------
    # Label creation
    # ------------------------------------------------------------------

    def make_label(self, label: Label, plate: LidPlate) -> Bosl2Solid | None:
        """Build a label solid for *label*, fitted to the lid *plate*.

        Uses the label's own :class:`~labels.LabelOptions` directly (only the material
        colour is defaulted to the box's). Position and size default to the plate's
        footprint, so the label lands on the face being decorated whatever shape it is."""
        from lids_base import MakeLidLabel

        opts = label.options
        effective_colour = (
            self.material_colour if opts.material_colour == default_material_colour else opts.material_colour
        )
        options = replace(opts, material_colour=effective_colour)

        calc_size = list(label.size) if label.size else list(plate.size)
        origin = [plate.origin[0], plate.origin[1], 0.0]

        # A SHAPE image instead of text: extrude it to the lid thickness, colour it the LABEL
        # colour (a contrasting second material, like the text label -- NOT the body colour),
        # and centre it on the plate (or the caller's position). The caller pre-sizes the shape.
        if label.shape is not None:
            from components import _extrude_image

            pos = (
                list(label.position)
                if label.position
                else [origin[0] + plate.size[0] / 2, origin[1] + plate.size[1] / 2, 0]
            )
            return _extrude_image(label.shape, plate.thickness).color(opts.label_colour).translate(pos)

        calc_pos = list(label.position) if label.position else origin
        piece = MakeLidLabel(
            size=calc_size,
            lid_thickness=plate.thickness,
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

    Two things do NOT survive a type switch, and both fail loudly rather than quietly:
    ``type_options`` belongs to one box type (the new type rejects it with a
    ``TypeError`` naming the class it wanted), and a switch to a type with
    ``has_lid = False`` (NoLidBox, PathBox, HingeBox) makes every ``make_lid()`` call
    raise. Keep ``type_options`` on the individual boxes that need it, not in the kit,
    if you want the one-word switch to stay a one-word switch.

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
