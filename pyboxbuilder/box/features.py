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

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

FIT_SLACK_MM = 0.2
"""Clearance between a lid and the feature it seats into, per side."""

PRINT_IN_PLACE_GAP_MM = 0.4
"""Gap between two parts printed as one piece, so they separate."""


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

    wt = spec.get("wall_thickness", 2.0)
    lt = spec.get("lid_thickness", 2.0)

    x = spec["width"] - wt - radius * 2
    z = spec["height"] - lt / 2

    dimple = sphere(radius=radius + FIT_SLACK_MM / 2)
    bump = sphere(radius=radius)
    return Closure(
        body=dimple.translate([x, wt, z]) | dimple.translate([x, spec["length"] - wt, z]),
        lid=bump.translate([x, wt, z]) | bump.translate([x, spec["length"] - wt, z]),
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
    if lid_thickness is None:
        lid_thickness = spec.get("lid_thickness", 2.0)

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
        knuckle = cylinder(height=length, radius=radius).rotate([0, 90, 0])
        knuckle = knuckle.translate([centre_x, axis_y, axis_z])

        # Each leaf webs back to its own half — the body's below the joint, the
        # lid's above it — so neither reaches across into the other.
        if index % 2:
            # Sized to the lid's own thickness — a taller web would stand proud
            # of the closed lid.
            web = block(
                [length, web_depth, lid_thickness - gap / 2],
                at=(centre_x - length / 2, web_y, axis_z + gap / 2),
            )
            lid_parts += [knuckle, web]
        else:
            web = block(
                [length, web_depth, radius],
                at=(centre_x - length / 2, web_y, axis_z - radius - gap / 2),
            )
            body_parts += [knuckle, web]

    pin = cylinder(height=spec["width"] + 2, radius=bore).rotate([0, 90, 0])
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


def path_cap(spec: dict, path, cap_height: float) -> "Bosl2Solid":
    """A cap whose skirt follows a polygon footprint instead of a rectangle."""
    lt = spec.get("lid_thickness", 2.0)
    slack = FIT_SLACK_MM

    outer_path = offset_footprint(path, -(spec.get("wall_thickness", 2.0) + slack))
    cavity_path = offset_footprint(path, -slack)

    base = spec["height"] - cap_height
    cap = extrude_footprint(outer_path, lt + cap_height, base)
    cavity = extrude_footprint(cavity_path, cap_height, base)
    return cap - cavity


def path_sleeve(spec: dict, path, slip: float, foot: float = 0.0) -> "Bosl2Solid":
    """A sleeve that slips over a polygon-footprint body, stopping at the foot."""
    lt = spec.get("lid_thickness", 2.0)
    skirt = spec["height"] - foot

    outer = extrude_footprint(offset_footprint(path, -slip), lt + skirt, foot)
    cavity = extrude_footprint(offset_footprint(path, -FIT_SLACK_MM), skirt, foot)
    return outer - cavity
