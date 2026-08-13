# SPDX-License-Identifier: Apache-2.0
"""Box type registry — maps BoxType enum to implementation classes."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyboxbuilder.enums import BoxType

if TYPE_CHECKING:
    from pyboxbuilder.box.base import BoxProtocol


@dataclass
class _RegistryEntry:
    box_class: type["BoxProtocol"]
    builder_class: type


BOX_TYPE_REGISTRY: dict[BoxType, type] = {}
"""Maps BoxType enum members to their BoxBuilder subclass."""

BOX_IMPL_REGISTRY: dict[BoxType, type] = {}
"""Maps BoxType enum members to their BoxProtocol implementation."""


def register_box(
    box_type: BoxType,
    builder_class: type,
    box_class: type | None = None,
) -> None:
    """Register a box type with its builder and optional implementation.

    Args:
        box_type: The BoxType enum member.
        builder_class: The BoxBuilder subclass for this type.
        box_class: The BoxProtocol implementation (can be registered later).
    """
    BOX_TYPE_REGISTRY[box_type] = builder_class
    if box_class is not None:
        BOX_IMPL_REGISTRY[box_type] = box_class


# Register available box types
from pyboxbuilder.builders.sliding import SlidingBoxBuilder  # noqa: E402
from pyboxbuilder.builders.cap import CapBoxBuilder  # noqa: E402
from pyboxbuilder.builders.hinge import HingeBoxBuilder  # noqa: E402
from pyboxbuilder.builders.filament_hinge import FilamentHingeBoxBuilder  # noqa: E402
from pyboxbuilder.builders.magnetic import MagneticBoxBuilder  # noqa: E402
from pyboxbuilder.builders.inset import InsetBoxBuilder  # noqa: E402
from pyboxbuilder.builders.sliding_catch import SlidingCatchBoxBuilder  # noqa: E402
from pyboxbuilder.builders.slipover import SlipoverBoxBuilder  # noqa: E402
from pyboxbuilder.builders.slipover_path import SlipoverPathBoxBuilder  # noqa: E402
from pyboxbuilder.builders.cap_path import CapPathBoxBuilder  # noqa: E402
from pyboxbuilder.builders.no_lid import NoLidBoxBuilder  # noqa: E402
from pyboxbuilder.builders.path import PathBoxBuilder  # noqa: E402
from pyboxbuilder.builders.card_library import CardLibraryBoxBuilder  # noqa: E402

from pyboxbuilder.box.types.sliding import SlidingBox  # noqa: E402
from pyboxbuilder.box.types.cap import CapBox  # noqa: E402
from pyboxbuilder.box.types.hinge import HingeBox  # noqa: E402
from pyboxbuilder.box.types.filament_hinge import FilamentHingeBox  # noqa: E402
from pyboxbuilder.box.types.magnetic import MagneticBox  # noqa: E402
from pyboxbuilder.box.types.inset import InsetBox  # noqa: E402
from pyboxbuilder.box.types.sliding_catch import SlidingCatchBox  # noqa: E402
from pyboxbuilder.box.types.slipover import SlipoverBox  # noqa: E402
from pyboxbuilder.box.types.slipover_path import SlipoverPathBox  # noqa: E402
from pyboxbuilder.box.types.cap_path import CapPathBox  # noqa: E402
from pyboxbuilder.box.types.no_lid import NoLidBox  # noqa: E402
from pyboxbuilder.box.types.path import PathBox  # noqa: E402
from pyboxbuilder.box.types.card_library import CardLibraryBox  # noqa: E402

register_box(BoxType.SLIDING, SlidingBoxBuilder, SlidingBox)
register_box(BoxType.CAP, CapBoxBuilder, CapBox)
register_box(BoxType.HINGE, HingeBoxBuilder, HingeBox)
register_box(BoxType.FILAMENT_HINGE, FilamentHingeBoxBuilder, FilamentHingeBox)
register_box(BoxType.MAGNETIC, MagneticBoxBuilder, MagneticBox)
register_box(BoxType.INSET, InsetBoxBuilder, InsetBox)
register_box(BoxType.SLIDING_CATCH, SlidingCatchBoxBuilder, SlidingCatchBox)
register_box(BoxType.SLIPOVER, SlipoverBoxBuilder, SlipoverBox)
register_box(BoxType.SLIPOVER_PATH, SlipoverPathBoxBuilder, SlipoverPathBox)
register_box(BoxType.CAP_PATH, CapPathBoxBuilder, CapPathBox)
register_box(BoxType.NO_LID, NoLidBoxBuilder, NoLidBox)
register_box(BoxType.PATH, PathBoxBuilder, PathBox)
register_box(BoxType.CARD_LIBRARY, CardLibraryBoxBuilder, CardLibraryBox)


LIDLESS_BOX_TYPES: frozenset[BoxType] = frozenset({BoxType.NO_LID, BoxType.PATH})
"""Box types that produce a body file only — no lid geometry, no `_lid.3mf`."""
