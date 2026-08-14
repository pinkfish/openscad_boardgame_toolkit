# SPDX-License-Identifier: Apache-2.0
"""Turn a laid-out set of compartments into the solid that gets cut from a body.

`layout_compartments` decides *where* things go; this module builds *what* is
removed. It handles three kinds of compartment:

* a plain rectangular well (optionally with rounded corners and a finger scoop),
* a silhouette well driven by `shape_file`,
* an element pack — many individual silhouettes at their own offsets, rotations
  and depths inside one bounding box (FR-004b).

Everything is returned in the box's own coordinate frame, so a caller only has
to subtract it from the body.
"""

from __future__ import annotations

from pyboxbuilder.precision import kwargs as precision_kwargs
from pyboxbuilder.rounding import round_edges, rounding_facets, vertical_edges

from typing import TYPE_CHECKING, Sequence

from pyboxbuilder.box.interior import Interior
from pyboxbuilder.enums import ScoopSide

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

    from pyboxbuilder.compartments.layout import CompartmentPlacement


def compartment_floor_z(placement: "CompartmentPlacement", interior: Interior) -> float:
    """Z of a compartment's floor.

    Wells are cut from the top down: the floor sits `depth` below the interior
    ceiling, so shallow compartments sit high in the box and their pieces stay
    within reach, matching the original toolkit's `$inner_height - depth` idiom.
    """
    depth = min(placement.depth, interior.height)
    return interior.origin_z + interior.height - depth


def build_compartment_well(
    placement: "CompartmentPlacement",
    interior: Interior,
    *,
    rounded_corners: float = 0.0,
    bottom_rounding: float = 0.0,
) -> "Bosl2Solid":
    """Build a compartment's well — the part that stays inside the walls.

    Args:
        placement: Where and how big the well is.
        interior: The box interior it sits in.
        rounded_corners: Radius for the well's vertical corners.
        bottom_rounding: Radius where the well's walls meet its floor. A tray
            wants this — pieces ride up the curve instead of having to be
            picked out of a square corner — while a card slot wants ``0``, so
            the stack sits flat on the floor.

    Returns:
        The cutout, positioned in the box frame.
    """
    from pybosl2 import Anchor, cuboid

    from pyboxbuilder.compartments.element import build_element_pack, svg_solid

    width, length = placement.size
    depth = min(placement.depth, interior.height)

    if placement.elements:
        # An element pack positions its own members; it is already corner-based.
        well = build_element_pack(placement.elements, depth)
        assert well is not None  # non-empty by the branch condition
        return _place(well, placement, interior)

    if placement.shape_file:
        well = svg_solid(placement.shape_file, width, length, depth)
    else:
        # The two radii differ, and a cuboid carries one, so the floor fillet is
        # built in and the vertical corners are taken off afterwards. Both make
        # the *void* smaller, which is what leaves material as a fillet.
        if bottom_rounding > 0 and bottom_rounding < min(width, length, depth) / 2:
            well = cuboid([width, length, depth], rounding=bottom_rounding,
                          edges=Anchor.BOTTOM, **rounding_facets())
        else:
            well = cuboid([width, length, depth])
        if rounded_corners > 0:
            well = round_edges(
                well, [width, length, depth], rounded_corners, vertical_edges(),
                at=(-width / 2, -length / 2, -depth / 2),
            )

    # pybosl2 primitives are centre-anchored; shift so the well's lower-left
    # corner and floor land on the placement.
    return _place(well.translate([width / 2, length / 2, depth / 2]), placement, interior)


def build_compartment_scoop(
    placement: "CompartmentPlacement",
    interior: Interior,
    scoop_side: ScoopSide = ScoopSide.FRONT,
) -> "Bosl2Solid":
    """Build a compartment's finger scoop — the part that pierces a wall.

    The wall thickness is read off the interior frame (its origin is inset by
    exactly one wall), because the scoop's face fillets are produced by flaring
    the sweep's ends and therefore need the sweep to match the wall it crosses.

    Args:
        placement: The compartment the scoop belongs to.
        interior: The box interior frame the compartment sits in.
        scoop_side: Which wall the scoop pierces.

    Returns:
        The scoop cutout, positioned in the box frame.
    """
    from pyboxbuilder.compartments.finger_hole import build_scoop

    width, length = placement.size
    depth = min(placement.depth, interior.height)
    wall_thickness = interior.origin_x if interior.origin_x > 0 else 2.0
    # origin_z is the box floor: the scoop dips a fraction of it so its bottom
    # face is not coplanar with the well floor (which renders as speckle).
    scoop = build_scoop(
        width, length, depth, scoop_side,
        wall_thickness=wall_thickness,
        floor_thickness=interior.origin_z if interior.origin_z > 0 else None,
    )
    return _place(scoop, placement, interior)


def _place(
    solid: "Bosl2Solid", placement: "CompartmentPlacement", interior: Interior
) -> "Bosl2Solid":
    """Move a compartment-local solid into the box frame."""
    return solid.translate([
        placement.position[0],
        placement.position[1],
        compartment_floor_z(placement, interior),
    ])


TRAY_ROUNDING_RATIO = 2.0 / 3.0
"""A tray well's default radius, as a fraction of its own depth.

Sized off the *cutout*, not off the box: what makes a piece easy to get out is
the curve your finger follows up the wall, so a deep well wants a big sweep and
a shallow token tray a small one. A box-wide constant gets both wrong.
"""


def tray_rounding(placement: "CompartmentPlacement", builder: object) -> float:
    """The radius for a tray well's vertical corners and its floor.

    Returns ``0`` for anything whose shape is dictated by what it holds — a
    card slot, an SVG silhouette, an element pack. Those are game-specific
    geometry: a card stack needs a flat floor and square corners to sit in,
    and a silhouette's outline is reproduced as authored (FR-045). Rounding is
    for the generic wells that hold loose pieces.

    Args:
        placement: The well being carved.
        builder: Its :class:`CompartmentBuilder`, if it has one. ``None`` (a
            bare placement) is treated as a tray.

    Returns:
        The radius in mm: ``depth × 2/3``, capped so it can neither swallow the
        well's footprint nor exceed its depth.
    """
    if getattr(builder, "holds_cards", False):
        return 0.0
    if getattr(builder, "shape_file", None) or getattr(builder, "elements", ()):
        return 0.0

    explicit = getattr(builder, "rounded_corners", 0.0) or 0.0
    radius = explicit if explicit > 0 else placement.depth * TRAY_ROUNDING_RATIO

    width, length = placement.size
    # A radius at least half the footprint has no straight side left to blend
    # into, and one deeper than the well would cut through its own floor.
    return max(0.0, min(radius, min(width, length) / 2 - 0.01, placement.depth))


def build_contents(
    placements: Sequence["CompartmentPlacement"],
    interior: Interior,
    builders: dict | None = None,
    clip: bool = True,
) -> "Bosl2Solid | None":
    """Union the cutouts for every placed compartment. None when there are none.

    Wells and finger scoops are treated differently on purpose: a well must stay
    inside the walls, while a scoop only works if it cuts through one. So the
    wells are clipped to the interior footprint and the scoops are added after.

    Args:
        placements: Output of `layout_compartments`.
        interior: The box interior the placements were laid out in.
        builders: Optional {label: CompartmentBuilder} so per-compartment
            options (rounded corners, finger scoops) are honoured.
        clip: Trim the wells to the interior footprint so none can break through
            a side wall (FR-018). Each well's own rounding comes from its depth
            and its builder — see :func:`tray_rounding`.
    """
    from pyboxbuilder.compartments.element import union_all

    builders = builders or {}
    wells = []
    scoops = []
    for placement in placements:
        builder = builders.get(placement.label)
        radius = tray_rounding(placement, builder)
        wells.append(
            build_compartment_well(
                placement, interior, rounded_corners=radius, bottom_rounding=radius,
            )
        )
        if getattr(builder, "finger_scoop", False):
            scoops.append(
                build_compartment_scoop(
                    placement,
                    interior,
                    getattr(builder, "scoop_side", ScoopSide.FRONT),
                )
            )

    contents = union_all(wells)
    if contents is not None and clip:
        contents = contents & interior_column(interior)
    if contents is not None:
        # Open the box. A compartmented box is carved out of a solid block, so
        # without this the material above the interior ceiling — the lid recess
        # on a cap box, the groove band on a sliding one — stays put and seals
        # every well under a lid of its own.
        contents = contents | interior_mouth(interior)

    scoop = union_all(scoops)
    if scoop is None:
        return contents
    return scoop if contents is None else contents | scoop


def interior_mouth(interior: Interior, headroom: float = 1000.0) -> "Bosl2Solid":
    """The open volume above the interior ceiling — the box's mouth.

    Runs from the ceiling up past the top of any box, so whatever the type puts
    between the interior and the rim is cleared away and the wells are reachable.
    """
    from pyboxbuilder.box.shell import block

    return block(
        [interior.width, interior.length, headroom],
        at=(
            interior.origin_x,
            interior.origin_y,
            interior.origin_z + interior.height,
        ),
    )


def interior_column(interior: Interior) -> "Bosl2Solid":
    """A tall prism over the interior footprint, used to clip compartments.

    Clipping is in X/Y only: a cutout must never break through a side wall, but
    it does have to run out through the top of the box, which is where pieces go
    in. This is the same guard the original toolkit applies by hand when a
    hexagon overhangs the interior — a hex laid out flat-to-flat is wider than
    its nominal width across the points, so it can poke through a wall.
    """
    from pybosl2 import cuboid

    tall = interior.height * 4 + 100.0
    return cuboid([interior.width, interior.length, tall]).translate([
        interior.origin_x + interior.width / 2,
        interior.origin_y + interior.length / 2,
        interior.origin_z + interior.height / 2,
    ])
