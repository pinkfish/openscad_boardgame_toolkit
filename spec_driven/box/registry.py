# SPDX-License-Identifier: Apache-2.0
"""Box type registry — maps BoxType enum to implementation classes."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_driven.enums import BoxType

if TYPE_CHECKING:
    from spec_driven.box.base import BoxProtocol


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
from spec_driven.builders.sliding import SlidingBoxBuilder  # noqa: E402
from spec_driven.box.types.sliding import SlidingBox  # noqa: E402

register_box(BoxType.SLIDING, SlidingBoxBuilder, SlidingBox)
