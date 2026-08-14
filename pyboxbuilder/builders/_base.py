# SPDX-License-Identifier: Apache-2.0
"""BoxBuilder base class and registry stub."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from pybosl2 import Color

from pyboxbuilder.enums import BoxType, MagnetType, StackableMode

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
        scoop_side: "ScoopSide" = None,
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
            scoop_side=scoop_side or ScoopSide.FRONT,
            no_rotate=no_rotate,
            shape_file=shape_file,
            position=position,
            elements=elements,
            element_margin=element_margin,
        )
        object.__setattr__(self, "compartments", self.compartments + (cb,))
        return cb


@dataclass(frozen=True)
class FingerHoleBuilder:
    """Finger hole configuration for a box exterior wall."""

    side: str
    radius: float = 14.0
    depth: float = 6.0
