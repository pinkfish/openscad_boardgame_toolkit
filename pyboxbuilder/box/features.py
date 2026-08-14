# SPDX-License-Identifier: Apache-2.0
"""Reusable closure features shared by the box types (T162).

A lid only works if the body has the matching half of the same feature — a
rabbet needs a ledge cut for it, a sliding lid needs grooves the right depth,
a filament hinge needs knuckles that interleave and share a pin axis. Keeping
both halves of each feature in one function is what stops them drifting apart.

Everything is built in the box's own frame: (0, 0, 0) is its lower-left corner
at the bed. pybosl2 primitives are centre-anchored, so placement goes through
`shell.block` / `shell.corner`.
"""

from __future__ import annotations

from pyboxbuilder.precision import kwargs as precision_kwargs

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

FIT_SLACK_MM = 0.2
"""Clearance between a lid and the feature it seats into, per side."""

PRINT_IN_PLACE_GAP_MM = 0.4
"""Gap between two parts printed as one piece, so they separate."""

WIGGLE_MM = 0.2
"""Clearance between two printed parts that have to come apart again.

`m_piece_wiggle_room` in the original toolkit, and used the same way here.
"""


# --------------------------------------------------------- declared size

# A box's declared size is the outside of the CLOSED box -- lid on. That is the
# size the packer reserves space for, so a lid that adds to any dimension makes
# every layout wrong: it is not the box that was planned for. Both closures
# below therefore shrink the body to make room for the lid, rather than hanging
# the lid off the outside of a full-size body.


@dataclass(frozen=True)
class CapMetrics:
    """The numbers a cap box's body and lid must agree on.

    Derived once so the two halves cannot drift apart: the body's stepped-in top
    band is exactly what the lid's skirt wraps, and the lid's outer face is
    exactly the box's declared footprint.
    """

    body_height: float
    """Top of the body. The lid's plate sits above it, coming to `height`."""
    cap_height: float
    """How far the lid's skirt reaches down the outside of the body."""
    band_z: float
    """Where the body steps in to make room for that skirt."""
    band_width: float
    band_length: float
    inset: float
    """How far the band is set in from the declared footprint, per side."""


def cap_metrics(spec: dict) -> CapMetrics:
    """Work out a cap box's shared geometry from its declared size."""
    wt = spec.get("wall_thickness", 2.0)
    lt = spec.get("lid_thickness", 2.0)
    wiggle = spec.get("size_spacing", WIGGLE_MM)
    # The original's CapBoxDefaultCapHeight / CapBoxDefaultLidWallThickness.
    cap_h = spec.get("cap_height") or min(10.0, spec["height"] / 2)
    lid_wall = wt / 2

    inset = lid_wall + 0.75 * wiggle
    return CapMetrics(
        body_height=spec["height"] - lt - wiggle,
        cap_height=cap_h,
        band_z=spec["height"] - cap_h,
        band_width=spec["width"] - 2 * inset,
        band_length=spec["length"] - 2 * inset,
        inset=inset,
    )


def cap_body(spec: dict) -> "Bosl2Solid":
    """A cap box's body: full footprint below, stepped in for the skirt above."""
    from pyboxbuilder.box.shell import block, build_shell

    m = cap_metrics(spec)
    shell = build_shell({**spec, "height": m.body_height})
    if m.band_z >= m.body_height:
        return shell  # the cap is taller than the body; nothing to step in

    # Keep everything below the band at full size, and only the band above it.
    # The band is what the skirt grips, so its corners take the smaller mating
    # radius — matched by the lid's cavity in `cap_lid` — while everything below
    # it keeps the body's own outer rounding.
    from pyboxbuilder.rounding import mating_rounding, rounded_block, vertical_edges

    keep = block([spec["width"], spec["length"], m.band_z]) | rounded_block(
        [m.band_width, m.band_length, m.body_height - m.band_z],
        mating_rounding(spec),
        vertical_edges(),
        at=(m.inset, m.inset, m.band_z),
    )
    return shell & keep


def cap_lid(spec: dict) -> "Bosl2Solid":
    """A cap box's lid: a plate whose skirt grips the body's stepped-in band.

    Its outer face is the declared footprint and its top is the declared height,
    so a closed cap box measures exactly what it was asked for.
    """
    from pyboxbuilder.box.shell import block

    m = cap_metrics(spec)
    lt = spec.get("lid_thickness", 2.0)
    slack = spec.get("cap_slack", WIGGLE_MM)

    from pyboxbuilder.rounding import mating_rounding, rounded_block, vertical_edges

    outer = block(
        [spec["width"], spec["length"], m.cap_height], at=(0.0, 0.0, m.band_z)
    )
    # The cavity's corners are rounded to the same radius as the band they slide
    # over, so the two nest instead of meeting at a gap.
    cavity = rounded_block(
        [m.band_width + 2 * slack, m.band_length + 2 * slack, m.cap_height - lt],
        mating_rounding(spec),
        vertical_edges(),
        at=(m.inset - slack, m.inset - slack, m.band_z),
    )
    return outer - cavity


def slipover_metrics(spec: dict) -> tuple[float, float]:
    """(inset per side, body height) for a slipover box.

    The sleeve's outer face is the declared footprint, so the body is set in by
    a wall thickness all round and stops a lid thickness short.
    """
    wt = spec.get("wall_thickness", 2.0)
    lt = spec.get("lid_thickness", 2.0)
    wiggle = spec.get("size_spacing", WIGGLE_MM)
    return wt + wiggle, spec["height"] - lt - wiggle


@dataclass(frozen=True)
class Closure:
    """The two halves of a closure feature.

    `body` is cut from or added to the box; `lid` likewise for the lid. Which
    of the two applies is the caller's business — a rabbet subtracts its body
    half and adds its lid half, a knuckle adds both.
    """

    body: "Bosl2Solid | None" = None
    lid: "Bosl2Solid | None" = None


# ------------------------------------------------------------------- rabbet


def rabbet(spec: dict, inset: float = 1.0) -> Closure:
    """A ledge cut into the top rim, and the plate that drops into it.

    The lid finishes flush with the rim rather than sitting on top of it, which
    is what makes an inset box stackable.

    Args:
        spec: Box dimensions; reads `wall_thickness` and `lid_thickness`.
        inset: How far the ledge reaches in past the wall's inner face, so the
            lid has something to rest on rather than falling through.
    """
    from pyboxbuilder.box.shell import block

    wt = spec.get("wall_thickness", 2.0)
    lt = spec.get("lid_thickness", 2.0)
    ledge = max(wt - inset, 0.0)

    recess_w = spec["width"] - 2 * ledge
    recess_l = spec["length"] - 2 * ledge
    top = spec["height"] - lt

    return Closure(
        body=block([recess_w, recess_l, lt + 0.1], at=(ledge, ledge, top)),
        lid=block(
            [recess_w - 2 * FIT_SLACK_MM, recess_l - 2 * FIT_SLACK_MM, lt],
            at=(ledge + FIT_SLACK_MM, ledge + FIT_SLACK_MM, top),
        ),
    )


# ------------------------------------------------------------ sliding track


def groove_depth(spec: dict) -> float:
    """How far a sliding groove bites into the side wall.

    Capped so it always leaves material behind it — a groove as deep as the
    wall is a slot straight through the side of the box.
    """
    wt = spec.get("wall_thickness", 2.0)
    lt = spec.get("lid_thickness", 2.0)
    return min(wt - 0.6, lt)


def sliding_track(spec: dict) -> Closure:
    """Grooves down the two side walls, and the plate that slides in them."""
    from pyboxbuilder.box.shell import block

    wt = spec.get("wall_thickness", 2.0)
    lt = spec.get("lid_thickness", 2.0)
    depth = groove_depth(spec)
    groove_w = spec["width"] - 2 * wt
    groove_h = lt + 0.2
    groove_z = spec["height"] - lt - 0.1

    left = block([groove_w, depth, groove_h], at=(wt, wt - depth, groove_z))
    right = block([groove_w, depth, groove_h], at=(wt, spec["length"] - wt, groove_z))

    lid_l = spec["length"] - 2 * wt + 2 * depth - FIT_SLACK_MM
    lid = block(
        [groove_w, lid_l, lt],
        at=(wt, wt - depth + FIT_SLACK_MM / 2, spec["height"] - lt),
    )
    return Closure(body=left | right, lid=lid)


def sliding_catch(spec: dict, radius: float = 1.0) -> Closure:
    """A detent that clicks the sliding lid shut.

    A bump on the lid's leading edge drops into a dimple at the far end of the
    groove. The dimple is cut a touch larger so the two are not an interference
    fit — the lid should click, not jam.
    """
    from pybosl2 import sphere

    from pyboxbuilder.box.shell import block

    wt = spec.get("wall_thickness", 2.0)
    lt = spec.get("lid_thickness", 2.0)

    x = spec["width"] - wt - radius * 2
    z = spec["height"] - lt / 2

    dimple = sphere(radius=radius + FIT_SLACK_MM / 2, **precision_kwargs())
    bump = sphere(radius=radius, **precision_kwargs())
    bumps = bump.translate([x, wt, z]) | bump.translate([x, spec["length"] - wt, z])
    # The bump engages sideways in the groove, so trimming its crown at the box's
    # top face costs nothing — and leaving it proud would make the closed box
    # taller than its declared height. The dimple is left untrimmed: it is cut
    # from the body, and opening it slightly at the rim is harmless.
    envelope = block([spec["width"], spec["length"], spec["height"]])
    return Closure(
        body=dimple.translate([x, wt, z]) | dimple.translate([x, spec["length"] - wt, z]),
        lid=bumps & envelope,
    )


# ------------------------------------------------------------ filament hinge


def filament_hinge(
    spec: dict,
    filament_diameter: float = 1.75,
    knuckles: int = 5,
    lid_thickness: float | None = None,
) -> Closure:
    """Interleaved knuckles along the back edge, bored for a filament pin.

    The "hinge" is a length of filament threaded through the knuckles after
    printing, so the two halves stay separate parts. Both sets share one pin
    axis and alternate along it, with a print gap between neighbours.

    Args:
        spec: Box dimensions.
        filament_diameter: Pin stock diameter; the bore is a little wider.
        knuckles: Total knuckles across the hinge, alternating body and lid.
        lid_thickness: Thickness of the leaf the lid's knuckles web into;
            defaults to the spec's.
    """
    from pybosl2 import cylinder

    from pyboxbuilder.box.shell import block
    from pyboxbuilder.compartments.element import union_all

    wt = spec.get("wall_thickness", 2.0)
    radius = max(wt, filament_diameter)
    bore = filament_diameter / 2 + 0.2
    gap = PRINT_IN_PLACE_GAP_MM
    leaf_thickness = (
        spec.get("lid_thickness", 2.0) if lid_thickness is None else lid_thickness
    )

    # The pin runs along X, clear of the back wall and level with the joint
    # between body and lid. Keeping it fully outside matters: an axis sunk into
    # the wall buries the *lid's* knuckles in the body, fusing the two parts.
    axis_y = spec["length"] + radius + gap
    axis_z = spec["height"]

    span = spec["width"] - 2 * wt
    pitch = span / knuckles
    web_y = spec["length"] - 0.5
    web_depth = axis_y - web_y

    body_parts, lid_parts = [], []
    for index in range(knuckles):
        length = pitch - gap
        if length <= 0:
            continue
        centre_x = wt + pitch * (index + 0.5)
        knuckle = cylinder(height=length, radius=radius, **precision_kwargs()).rotate([0, 90, 0])
        knuckle = knuckle.translate([centre_x, axis_y, axis_z])

        # Each leaf webs back to its own half — the body's below the joint, the
        # lid's above it — so neither reaches across into the other.
        if index % 2:
            # Sized to the lid's own thickness — a taller web would stand proud
            # of the closed lid.
            web = block(
                [length, web_depth, leaf_thickness - gap / 2],
                at=(centre_x - length / 2, web_y, axis_z + gap / 2),
            )
            lid_parts += [knuckle, web]
        else:
            web = block(
                [length, web_depth, radius],
                at=(centre_x - length / 2, web_y, axis_z - radius - gap / 2),
            )
            body_parts += [knuckle, web]

    pin = cylinder(height=spec["width"] + 2, radius=bore, **precision_kwargs()).rotate([0, 90, 0])
    pin = pin.translate([spec["width"] / 2, axis_y, axis_z])
    # Split the barrel at the joint line so the two leaves cannot touch.
    parting = block(
        [spec["width"] + 2, web_depth + 2 * radius + 2, gap],
        at=(-1.0, web_y - 1.0, axis_z - gap / 2),
    )

    body = union_all(body_parts)
    lid = union_all(lid_parts)
    return Closure(
        body=None if body is None else body - pin - parting,
        lid=None if lid is None else lid - pin - parting,
    )


# --------------------------------------------------------------- path skirt


def offset_footprint(path, distance: float):
    """Grow or shrink a footprint outline by `distance` (positive shrinks)."""
    from pyboxbuilder.paths import inset_rectilinear, is_rectilinear

    if is_rectilinear(path):
        return inset_rectilinear(path, distance)

    cx = sum(p[0] for p in path) / len(path)
    cy = sum(p[1] for p in path) / len(path)
    out = []
    for x, y in path:
        dx, dy = x - cx, y - cy
        span = max((dx * dx + dy * dy) ** 0.5, 1e-9)
        scale = max(0.0, (span - distance) / span)
        out.append((cx + dx * scale, cy + dy * scale))
    return tuple(out)


def extrude_footprint(path, height: float, base_z: float = 0.0) -> "Bosl2Solid":
    """Extrude a footprint outline upward from `base_z`.

    `linear_extrude` is the one operation that already grows from its base
    rather than being centre-anchored, so this only has to lift it.
    """
    from pybosl2 import Path2D

    profile = Path2D([(float(x), float(y)) for x, y in path], closed=True)
    solid = profile.linear_extrude(height=height)
    return solid if base_z == 0.0 else solid.translate([0.0, 0.0, base_z])


def path_body_metrics(spec: dict) -> tuple[float, float]:
    """(inset per side, body height) for a polygon-footprint body.

    Same rule as the rectangular closures: the declared outline and height are
    the outside of the closed box, so the body is set in and stops short, and
    the cap or sleeve fills the difference back out to the declared size.
    """
    wt = spec.get("wall_thickness", 2.0)
    lt = spec.get("lid_thickness", 2.0)
    wiggle = spec.get("size_spacing", WIGGLE_MM)
    return wt / 2 + wiggle, spec["height"] - lt - wiggle


def path_cap(spec: dict, path, cap_height: float) -> "Bosl2Solid":
    """A cap whose skirt follows a polygon footprint instead of a rectangle.

    Its outer face is the declared outline, so a closed box measures exactly
    what it was asked for.
    """
    lt = spec.get("lid_thickness", 2.0)
    slack = spec.get("cap_slack", WIGGLE_MM)
    inset, _ = path_body_metrics(spec)

    base = spec["height"] - cap_height
    cap = extrude_footprint(path, cap_height, base)
    cavity = extrude_footprint(
        offset_footprint(path, inset - slack), cap_height - lt, base
    )
    return cap - cavity


def path_sleeve(spec: dict, path, slip: float, foot: float = 0.0) -> "Bosl2Solid":
    """A sleeve that slips over a polygon-footprint body, stopping at the foot."""
    lt = spec.get("lid_thickness", 2.0)
    slack = spec.get("slip_slack", WIGGLE_MM)
    inset, _ = path_body_metrics(spec)
    skirt = spec["height"] - foot

    outer = extrude_footprint(path, skirt, foot)
    cavity = extrude_footprint(
        offset_footprint(path, inset - slack), skirt - lt, foot
    )
    return outer - cavity
