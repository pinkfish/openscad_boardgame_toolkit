# SPDX-License-Identifier: Apache-2.0
"""Box protocol — abstract interface for box type implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


@dataclass(frozen=True)
class Interior:
    """The usable volume inside a box."""

    width: float
    length: float
    height: float
    origin_x: float = 0.0
    origin_y: float = 0.0
    origin_z: float = 0.0


class BoxProtocol(Protocol):
    """Interface that every box type implementation must satisfy.

    Simpler than the legacy BoxBaseType pipeline: no Body return type
    with hollowed/carved flags, no LidPlate contract.
    """

    def build_body(self, spec: "BoxSpec") -> "Bosl2Solid":
        """Build the box body geometry."""
        ...

    def build_lid(
        self, spec: "BoxSpec", decoration: "LidDecoration"
    ) -> "Bosl2Solid":
        """Build the lid geometry with decoration applied."""
        ...

    def interior(self, spec: "BoxSpec") -> Interior:
        """Compute the interior frame from the spec dimensions."""
        ...


def preferred_scoop_side(box: object, spec: dict):
    """Which wall this box type wants a finger scoop in.

    A hook rather than a rule, because only the type knows: on a sliding box
    the cut has to be in the wall the lid leaves by — the other three carry the
    lid, two of them holding the grooves it rides in.

    Args:
        box: The box type instance.
        spec: The box's spec dict.

    Returns:
        A :class:`ScoopSide`, or ``None`` for "no preference", which leaves the
        compartment's own shape to decide.
    """
    hook = getattr(box, "preferred_scoop_side", None)
    return hook(spec) if hook is not None else None


def lid_rounded_edges(box: object, spec: dict) -> list:
    """Which of this box type's lid edges may be rounded.

    Args:
        box: The box type instance.
        spec: The box's spec dict.

    Returns:
        A pybosl2 ``edges=`` selector. The default — four vertical corners and
        the top face — suits a lid that sits on top of the box, where all of
        that is on the outside. A lid that slides into the box overrides it.
    """
    from pyboxbuilder.rounding import vertical_and_top_edges

    hook = getattr(box, "lid_rounded_edges", None)
    return hook(spec) if hook is not None else vertical_and_top_edges()


def default_wall_top(spec: dict) -> float:
    """How high a wall stands when the box type says nothing about it.

    The box's own top face, less any band a lid occupies — so a cut merges
    into the surface a hand actually touches rather than into a plane buried
    under the lid.

    Args:
        spec: Reads `height`, `interior_top`, `rim_free` and `lid_thickness`.

    Returns:
        The z of the wall's top.
    """
    explicit = spec.get("interior_top")
    if explicit is not None:
        return float(explicit)
    lid_band = 0.0 if spec.get("rim_free") else (spec.get("lid_thickness", 0.0) or 0.0)
    return float(spec["height"]) - lid_band


def wall_tops(box: object, spec: dict) -> dict:
    """The z of each wall's top, per side.

    The four walls of a box do **not** have to end at the same height, and
    assuming they do is how a scoop ends up hanging in space: a sliding box's
    exit wall stops a lid thickness below the others, because that is where its
    channel runs out through it. Anything aligning to "the top" — a finger
    scoop's roll, a cut's trim — asks per side.

    Args:
        box: The box type instance, which may supply a `wall_tops` hook.
        spec: The box's spec dict.

    Returns:
        ``{ScoopSide: z}``, covering every side. Sides the type does not
        mention take :func:`default_wall_top`.
    """
    from pyboxbuilder.enums import ScoopSide

    fallback = default_wall_top(spec)
    tops = {side: fallback for side in ScoopSide}

    hook = getattr(box, "wall_tops", None)
    if hook is not None:
        for side, z in (hook(spec) or {}).items():
            tops[side] = float(z)
    return tops


def wall_top(spec: dict, side) -> float:
    """One wall's top, read from a spec that already carries the map.

    Args:
        spec: May carry a `wall_tops` mapping, as `Project` puts there.
        side: Which wall.

    Returns:
        That wall's top z, or :func:`default_wall_top` when the spec has no map.
    """
    tops = spec.get("wall_tops")
    if tops and side in tops:
        return float(tops[side])
    return default_wall_top(spec)
