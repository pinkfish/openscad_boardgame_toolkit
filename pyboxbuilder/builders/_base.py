# SPDX-License-Identifier: Apache-2.0
"""BoxBuilder base class and registry stub."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from pybosl2 import Color

from pyboxbuilder.enums import BoxType, MagnetType, ScoopSide, StackableMode

if TYPE_CHECKING:
    from pyboxbuilder.lid.builder import LidBuilder
    from pyboxbuilder.compartments.builder import CompartmentBuilder
    from pyboxbuilder.compartments.element import CompartmentElement



@dataclass(frozen=True)
class BoxBuilder:
    """Base builder for all box types.

    Carries common fields shared by every box type. Subclassed by
    type-specific builders that add their own typed fields.
    """

    box_type: ClassVar[BoxType]
    label: str
    """Box identifier, used for file naming."""
    box_id: str | None = None
    """Unique instance identifier; defaults to label."""
    size: tuple[float, float, float] | None = None
    """Box dimensions [W, L, H] in mm. None = auto-compute from compartments."""
    position: tuple[float, float, float] | None = None
    """Manual packing position override [X, Y, Z] in mm."""
    stackable: StackableMode | None = None
    """Interlocking rim mode for no-lid boxes; ``None`` means not stackable."""
    stackable_thickness: float | None = None
    """Interlocking rim thickness for stackable boxes."""
    magnet_type: MagnetType | None = None
    """Magnet slot shape; ``None`` or :attr:`MagnetType.NONE` means no magnets."""
    magnet_size: tuple[float, float, float] | None = None
    """Magnet slot dimensions [diameter_or_width, length, depth]."""
    final_size: tuple[float, float, float] | None = None
    """Resolved size after packing; set-once frozen during export."""
    expandable: bool = True
    """Box can be auto-sized larger during packing."""
    expandable_width: bool = True
    """Width axis can expand."""
    expandable_length: bool = True
    """Length axis can expand."""
    no_rotate: bool = False
    """Prevent 3D packer from rotating the box (keeps compartment layout directional)."""
    wall_thickness: float | None = None
    """Per-box wall thickness override; None uses project default."""
    floor_thickness: float | None = None
    """Per-box floor thickness override."""
    lid_thickness: float | None = None
    """Per-box lid thickness override."""
    rounding: float | None = None
    """Edge radius for this box's exposed edges; None uses the project default."""
    inner_rounding: float | None = None
    """Edge radius where a partial lid grips this body; None uses half the outer radius."""
    lid: LidBuilder | None = None
    """Lid decoration configuration."""
    color: Color | None = None
    """Body colour, as a :class:`pybosl2.Color` (webcolor names welcome).

    Used as the box's material colour on export and as its colour in
    :meth:`Project.show`. When unset, a preview assigns a stable pseudo-random
    hue derived from the label so adjacent boxes stay distinguishable; that
    fallback is view-time only and never reaches the exported geometry.
    """
    finger_holes: tuple[FingerHoleBuilder, ...] = ()
    """Finger holes on box exterior walls."""
    auto_finger_holes: bool = True
    """Let a lidless box cut its own default finger holes (FR-047).

    Only the no-lid and path types read this: when there are no explicit
    ``finger_holes``, they add a finger hole to each wall of their longer side,
    sized after the original. ``False`` opts out and leaves the walls plain.
    Lidded types ignore it.
    """
    compartments: tuple[CompartmentBuilder, ...] = ()
    """Interior compartments."""

    def __post_init__(self) -> None:
        """Reject bare strings where the API takes an enum.

        Type selections are enums throughout, so a stray ``"inside"`` or
        ``"round"`` is a mistake worth naming at construction rather than a
        silent no-match deep inside the geometry code.

        Raises:
            TypeError: If ``stackable`` or ``magnet_type`` is not its enum.
        """
        for name, enum_cls in (("stackable", StackableMode), ("magnet_type", MagnetType)):
            value = getattr(self, name)
            if value is not None and not isinstance(value, enum_cls):
                members = ", ".join(f"{enum_cls.__name__}.{m.name}" for m in enum_cls)
                raise TypeError(
                    f"Box '{self.label}': {name} must be a {enum_cls.__name__} "
                    f"({members}) or None; got {value!r}"
                )

    def compartment(
        self,
        label: str,
        *,
        size: tuple[float, float] | None = None,
        width_ratio: float | None = None,
        length_ratio: float | None = None,
        depth: float | None = None,
        rounded_corners: float = 0.0,
        finger_scoop: bool = False,
        scoop_side: "ScoopSide | None" = None,
        no_rotate: bool = False,
        shape_file: str | None = None,
        position: tuple[float, float] | None = None,
        elements: tuple[CompartmentElement, ...] = (),
        element_margin: float = 0.0,
    ) -> CompartmentBuilder:
        """Add a compartment to this box."""
        from pyboxbuilder.compartments.builder import CompartmentBuilder
        from pyboxbuilder.enums import ScoopSide

        cb = CompartmentBuilder(
            label=label,
            size=size,
            width_ratio=width_ratio,
            length_ratio=length_ratio,
            depth=depth,
            rounded_corners=rounded_corners,
            finger_scoop=finger_scoop,
            scoop_side=scoop_side,
            no_rotate=no_rotate,
            shape_file=shape_file,
            position=position,
            elements=elements,
            element_margin=element_margin,
        )
        object.__setattr__(self, "compartments", self.compartments + (cb,))
        return cb

    def finger_hole(
        self,
        side: "ScoopSide",
        *,
        radius: float = 14.0,
        depth: float | None = None,
        offset: float = 0.0,
        rounding_radius: float | None = None,
        rounding_edge: float | None = None,
    ) -> "FingerHoleBuilder":
        """Add a finger hole to one of this box's exterior walls (FR-006).

        The hole hangs from the rim, so a finger reaches in over the wall
        rather than through its middle, and it is cut with the same smoothing
        as a compartment scoop: a mouth flared into the rim and a fillet where
        it emerges on each face of the wall.

        Args:
            side: Which exterior wall to cut.
            radius: Bore radius in mm; 14mm is adult fingertip sizing.
            depth: How far down from the interior's top to reach. ``None``
                uses the radius. Capped at the interior depth so the cut
                cannot open the box's base.
            offset: Shift along the wall from its midpoint, in mm.
            rounding_radius: Mouth flare at the rim; ``None`` uses 3mm.
            rounding_edge: Face fillet; ``None`` uses ``wall_thickness / 2``,
                the largest the wall has room for.

        Returns:
            The :class:`FingerHoleBuilder` that was added, so it can be
            inspected; it is already registered on the box.

        Raises:
            TypeError: If ``side`` is not a :class:`ScoopSide`.
            ValueError: If ``radius`` or ``depth`` is not positive.
        """
        hole = FingerHoleBuilder(
            side=side,
            radius=radius,
            depth=depth,
            offset=offset,
            rounding_radius=rounding_radius,
            rounding_edge=rounding_edge,
        )
        object.__setattr__(self, "finger_holes", self.finger_holes + (hole,))
        return hole


@dataclass(frozen=True)
class FingerHoleBuilder:
    """A finger hole on a box's exterior wall (FR-006).

    Cut with the same builder as a compartment's wall scoop, so it gets the
    same mouth flare and face fillets: see
    :func:`pyboxbuilder.compartments.finger_hole.build_wall_scoop`.
    """

    side: ScoopSide
    """Which exterior wall the hole is cut through."""
    radius: float = 14.0
    """Bore radius in mm — adult fingertip sizing by default."""
    depth: float | None = None
    """How far down from the interior's top the cut reaches.

    ``None`` uses the radius, which is how the original sizes it: the height of
    a finger cut follows the finger, not the wall. A fixed default made every
    hole a shallow nick regardless of how big a finger it was cut for.
    """
    offset: float = 0.0
    """Shift along the wall from its midpoint, in mm."""
    rounding_radius: float | None = None
    """Mouth flare where the cut meets the rim; ``None`` uses the default 3mm."""
    rounding_edge: float | None = None
    """Fillet where the cut emerges on a face; ``None`` uses ``wall_thickness / 2``."""

    def __post_init__(self) -> None:
        """Validate the hole.

        Raises:
            TypeError: If ``side`` is not a :class:`ScoopSide` — a bare string
                would silently match no wall.
            ValueError: If ``radius`` or ``depth`` is not positive.
        """
        if not isinstance(self.side, ScoopSide):
            sides = ", ".join(f"ScoopSide.{m.name}" for m in ScoopSide)
            raise TypeError(f"finger hole side must be a ScoopSide ({sides}); got {self.side!r}")
        if self.radius <= 0:
            raise ValueError(f"finger hole radius must be > 0; got {self.radius}")
        if self.depth is not None and self.depth <= 0:
            raise ValueError(f"finger hole depth must be > 0; got {self.depth}")
