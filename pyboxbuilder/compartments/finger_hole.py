# SPDX-License-Identifier: Apache-2.0
"""Finger scoop and notch geometry for compartment walls and floors.

Ported from the original toolkit's ``FingerHoleWall`` and ``FingerHoleBase``
(``components.scad``), which are the reference for how a finger cut is meant to
be smoothed. Three separate roundings are at work, and they are easy to
conflate:

1. **The mouth** (``rounding_radius``) — the top of the profile flares outward
   into the compartment rim with a pair of concave fillets, so the opening
   curves into the wall instead of ending in a right-angle lip. This is the
   part a fingertip actually rides over.
2. **The faces** (``rounding_edge``) — the sweep's two ends get a *negative*
   (concave) rim, so where the cut emerges on each side of the wall it flows
   onto that face tangentially rather than leaving a sharp shadow line. Each
   face is independently switchable, because the outside of a box wants the
   softening far more than a compartment-internal divider does.
3. **The base** — a floor scoop additionally fillets the cut into the floor
   plane, so the bottom of the cut blends into the box's inside surface.

Both helpers return cutouts in the compartment's own frame: (0, 0, 0) is the
compartment's lower-left corner at its floor, the footprint runs out to
(comp_width, comp_length), and +Z is up towards the rim.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from pyboxbuilder.enums import ScoopSide
from pyboxbuilder.precision import kwargs as precision_kwargs
from pyboxbuilder.sweep import offset_sweep

if TYPE_CHECKING:
    from pybosl2.shapes2d import Bosl2Shape2D
    from pybosl2.shapes3d import Bosl2Solid

MIN_WALL_SCOOP_DEPTH_MM = 8.0
"""Below this a wall notch has nothing to grip, so the floor scoop is used."""

DEFAULT_MOUTH_ROUNDING_MM = 3.0
"""Flare at the top of a scoop where it meets the rim (the original's default)."""

DEFAULT_EDGE_ROUNDING_MM = 1.0
"""Fallback face fillet where no wall thickness is known.

The scoops normally derive it as ``wall_thickness / 2`` instead, which is what
the original passes and the largest fillet a wall has room for.
"""

_SIDE_CENTRES = {
    ScoopSide.FRONT: lambda w, l: (w / 2, 0.0),
    ScoopSide.BACK: lambda w, l: (w / 2, l),
    ScoopSide.LEFT: lambda w, l: (0.0, l / 2),
    ScoopSide.RIGHT: lambda w, l: (w, l / 2),
}

# Rotation about Z that turns the front-facing profile to face each side. The
# profile is built in the X-Z plane and swept along -Y — outward through the
# FRONT wall — so each spin has to carry that outward direction to the right
# side. Spin 90 maps (x, y) to (-y, x), which sends -Y to +X: that is RIGHT,
# not LEFT. Getting these backwards leaves the cut inside the compartment,
# shaving the wall's inner face by the sweep's 0.015 of fudge and piercing
# nothing — invisible in a bounding box, which is how it survived once.
_SIDE_SPIN = {
    ScoopSide.FRONT: 0.0,
    ScoopSide.BACK: 180.0,
    ScoopSide.LEFT: 270.0,
    ScoopSide.RIGHT: 90.0,
}


def scoop_profile(
    radius: float,
    height: float,
    rounding_radius: float = DEFAULT_MOUTH_ROUNDING_MM,
) -> "Bosl2Shape2D":
    """Build the 2-D side profile of a finger scoop, in the X-Z plane.

    A semicircular bottom of ``radius``, a straight throat up to ``height``,
    and a mouth that flares out by ``rounding_radius`` at the rim. Ported from
    ``FingerHoleWall``, including its two cases: when the scoop is too shallow
    for a straight throat, the mouth's fillet is blended into the bottom circle
    along their **common tangent**, which keeps the profile smooth instead of
    letting the two arcs cross at a corner.

    Args:
        radius: Radius of the finger bore — the widest part of the throat.
        height: Height from the floor to the rim.
        rounding_radius: Flare at the mouth. ``0`` gives a square-topped slot.

    Returns:
        The profile as 2-D geometry, with the floor at ``y=0`` and the rim at
        ``y=height``, centred on ``x=0``.

    Raises:
        ValueError: If ``radius`` or ``height`` is not positive, or
            ``rounding_radius`` is negative.
    """
    from pybosl2 import geometry, shapes2d

    if radius <= 0:
        raise ValueError(f"scoop radius must be > 0; got {radius}")
    if height <= 0:
        raise ValueError(f"scoop height must be > 0; got {height}")
    if rounding_radius < 0:
        raise ValueError(f"rounding_radius must be >= 0; got {rounding_radius}")

    bore = shapes2d.circle(radius=radius, **precision_kwargs()).translate([0.0, radius])

    if rounding_radius == 0:
        throat = shapes2d.square([radius * 2, height], center=True).translate([0.0, height / 2])
        return bore | throat

    if height >= radius + rounding_radius:
        # Room for a straight throat: bore, throat, and a flared mouth built as
        # a band the full flared width minus a fillet circle at each shoulder.
        throat_height = height - radius
        throat = shapes2d.square([radius * 2, throat_height], center=True).translate(
            [0.0, radius + throat_height / 2]
        )
        band = shapes2d.square(
            [radius * 2 + rounding_radius * 2, rounding_radius], center=True
        ).translate([0.0, height - rounding_radius / 2])
        mouth = band
        for direction in (1, -1):
            mouth = mouth - shapes2d.circle(
                radius=rounding_radius, **precision_kwargs()
            ).translate([direction * (radius + rounding_radius), height - rounding_radius])
        return bore | throat | mouth

    # Too shallow for a throat. Blend the shoulder fillet into the bore along
    # their common tangent (the original's circle_circle_tangents call), so the
    # two arcs meet smoothly rather than crossing.
    tangents = geometry.circle_circle_tangents(
        radius1=rounding_radius,
        center1=[radius + rounding_radius, height - rounding_radius],
        radius2=radius,
        center2=[0.0, radius],
    )
    if not tangents:
        # Circles too close for a common tangent — fall back to the square
        # mouth rather than emitting a broken profile.
        throat = shapes2d.square([radius * 2, height], center=True).translate([0.0, height / 2])
        return bore | throat

    start, end = tangents[-1]
    wedge = shapes2d.polygon([
        [float(start[0]), float(start[1])],
        [float(end[0]), float(end[1])],
        [float(radius + rounding_radius), float(height)],
        [0.0, float(height)],
        [0.0, float(start[1])],
    ])
    shoulder = shapes2d.square(
        [rounding_radius, rounding_radius], center=True
    ).translate([
        radius + rounding_radius / 2, height - rounding_radius / 2,
    ]) - shapes2d.circle(radius=rounding_radius, **precision_kwargs()).translate(
        [radius + rounding_radius, height - rounding_radius]
    )

    half = wedge | shoulder
    profile = bore | half | half.mirror([1, 0])
    # Clip to the flared envelope so no fillet construction pokes out.
    envelope = shapes2d.square(
        [radius * 2 + rounding_radius * 2, height], center=True
    ).translate([0.0, height / 2])
    return profile & envelope


def build_wall_scoop(
    comp_width: float,
    comp_length: float,
    comp_depth: float,
    side: ScoopSide,
    radius: float = 12.0,
    wall_thickness: float = 2.0,
    rounding_radius: float = DEFAULT_MOUTH_ROUNDING_MM,
    rounding_edge: float | None = None,
    round_inner: bool = True,
    round_outer: bool = True,
    breach_floor: bool = False,
    floor_thickness: float | None = None,
    floor_clearance: float | None = None,
) -> "Bosl2Solid":
    """Build a finger notch through a compartment wall.

    The profile from :func:`scoop_profile` swept through the wall, with a
    concave rim on each end so the cut flows onto the wall's faces instead of
    ending in a sharp line (``FingerHoleWall``'s ``rounding_edge``).

    **The sweep is exactly the wall thickness, centred on the wall** (the
    original passes ``depth_of_hole = wall_thickness + 0.03``), and that is
    load-bearing rather than incidental: a face fillet is produced by flaring
    the sweep's *end*, so the end has to coincide with the face. Overshooting
    the wall by a millimetre — the obvious way to make sure a boolean leaves no
    skin — puts both fillets out in the air beyond the box and leaves the cut
    meeting the faces at a hard edge after all. The 0.03 of fudge is the whole
    margin available.

    The sweep runs from the compartment floor to the rim, so a finger can reach
    the last card at the bottom of the stack, and is clipped at the floor plane
    so the box's base is not breached from the outside.

    Args:
        comp_width: Compartment footprint width.
        comp_length: Compartment footprint length.
        comp_depth: Compartment depth; the scoop runs its full height.
        side: Which wall to notch.
        radius: Notch radius in mm, capped so it cannot swallow the compartment.
        wall_thickness: Wall the cut passes through. Sets the sweep depth and,
            by default, the face fillet.
        rounding_radius: Flare at the mouth where the cut meets the rim.
        rounding_edge: Fillet where the cut emerges on a face. Defaults to
            ``wall_thickness / 2``, the largest fillet the wall has room for
            (and what the original uses). ``0`` squares the edge.
        round_inner: Fillet the compartment-side face.
        round_outer: Fillet the outward face — the visible outside of the box.
        breach_floor: Let the cut run as deep as the flare naturally reaches,
            with no clip at all. Off by default.
        floor_thickness: The box floor under this compartment. Used to size the
            dip below the well floor (half the floor, at most 1mm), which is
            what keeps the cut's bottom face off the floor plane.
        floor_clearance: Dip below the well floor, overriding the value derived
            from ``floor_thickness``. ``0`` clips exactly at the floor, at the
            cost of a coincident face.

    Returns:
        Bosl2Solid cutout, positioned in the compartment frame.

    Raises:
        ValueError: If the compartment or wall dimensions are not positive.
    """
    if comp_depth <= 0:
        raise ValueError(f"comp_depth must be > 0; got {comp_depth}")
    if wall_thickness <= 0:
        raise ValueError(f"wall_thickness must be > 0; got {wall_thickness}")

    span = comp_width if side in (ScoopSide.FRONT, ScoopSide.BACK) else comp_length
    radius = min(radius, span / 2)
    # The mouth flare widens the cut by rounding_radius each side; keep the
    # whole thing inside the compartment's span.
    rounding_radius = max(0.0, min(rounding_radius, span / 2 - radius))

    if rounding_edge is None:
        rounding_edge = wall_thickness / 2

    # Just the wall, plus a hair at each face so the boolean has no coincident
    # plane to resolve. See the note above on why this must not be larger.
    fudge = 0.03
    depth = wall_thickness + fudge
    rim = max(0.0, min(rounding_edge, (depth - 0.01) / 2))

    profile = scoop_profile(radius, comp_depth, rounding_radius)
    swept = offset_sweep(
        profile,
        height=depth,
        rounding_bottom=-rim if round_outer else 0.0,
        rounding_top=-rim if round_inner else 0.0,
    )

    # The profile is built in X-Z and extruded along +Z. Stand it up so the
    # extrusion runs along -Y (into the wall), then shift it so it spans the
    # wall from just outside the outer face to just inside the inner one.
    standing = swept.rotate([90.0, 0.0, 0.0]).translate([0.0, fudge / 2, 0.0])

    if not breach_floor:
        # Clip the cut just *below* the well floor. The flare is isotropic in
        # the profile plane, so it grows downwards past the bore as readily as
        # sideways, and left alone it would thin the floor by the fillet.
        #
        # The clip does not sit exactly on the floor plane, though: that leaves
        # the cut's bottom face coplanar with the floor, and a coincident face
        # renders as speckle and is the classic way a boolean leaves a
        # zero-thickness skin. The original's answer is to overshoot into the
        # floor by about a millimetre; this does the same, bounded by half the
        # floor so the box's base is still solid underneath.
        from pybosl2 import cuboid

        dip = floor_clearance if floor_clearance is not None else (
            min(1.0, floor_thickness / 2) if floor_thickness else 0.2
        )
        dip = max(0.0, dip)
        reach = comp_depth + rounding_radius + rim + 1.0
        keep = cuboid([span * 2 + radius * 4, depth * 4, reach * 2]).translate(
            [0.0, 0.0, reach - dip]
        )
        standing = standing & keep

    oriented = standing.rotate([0.0, 0.0, _SIDE_SPIN[side]])
    x, y = _SIDE_CENTRES[side](comp_width, comp_length)
    return oriented.translate([x, y, 0.0])


def build_floor_scoop(
    comp_width: float,
    comp_length: float,
    side: ScoopSide,
    radius: float = 14.0,
    comp_depth: float | None = None,
    wall_thickness: float = 2.0,
    rounding_radius: float = DEFAULT_MOUTH_ROUNDING_MM,
    rounding_edge: float | None = None,
    floor_thickness: float | None = None,
) -> "Bosl2Solid":
    """Build a scoop that blends into the compartment floor, at one edge.

    Ported from ``FingerHoleBase``, which is the shallow-compartment case: a
    wall notch in a 4mm wall gives a finger nothing to bite, so the cut is
    taken into the *floor* instead. Three parts, matching the original:

    1. the bore itself, running the compartment's full depth;
    2. a mouth flared into the rim, as on a wall scoop;
    3. a fillet blending the cut into the floor plane, so the bottom of the
       scoop curves into the box's inside surface rather than meeting it at a
       right angle.

    The floor fillet is what distinguishes this from a plain dish, and it is
    sized off the wall thickness (the original uses ``wall_thickness / 2``) so
    it stays proportionate to the box rather than to the finger.

    Args:
        comp_width: Compartment footprint width.
        comp_length: Compartment footprint length.
        side: Which edge the scoop sits against.
        radius: Bore radius in mm, capped to half the compartment's span.
        comp_depth: Compartment depth. Defaults to ``radius`` when unknown.
        wall_thickness: Wall the cut passes through; also sets the floor fillet.
        rounding_radius: Flare at the mouth where the cut meets the rim.
        rounding_edge: Fillet where the cut emerges on a face.

    Returns:
        Bosl2Solid cutout, positioned in the compartment frame. It reaches down
        to the floor plane and no further, so the box's base stays intact.

    Raises:
        ValueError: If the compartment span is not positive.
    """
    from pybosl2 import cuboid

    span = comp_width if side in (ScoopSide.FRONT, ScoopSide.BACK) else comp_length
    if span <= 0:
        raise ValueError(f"compartment span must be > 0; got {span}")

    radius = min(radius, span / 2)
    depth = comp_depth if comp_depth and comp_depth > 0 else radius

    # Parts 1 and 2: the same swept, face-filleted, flare-mouthed cut a wall
    # scoop uses. A shallow compartment reaches scoop_profile's tangent-blend
    # branch, which is exactly the case that branch exists for.
    cut = build_wall_scoop(
        comp_width, comp_length, depth, side,
        radius=radius,
        wall_thickness=wall_thickness,
        rounding_radius=rounding_radius,
        rounding_edge=rounding_edge,
        floor_thickness=floor_thickness,
    )

    # Part 3: blend the cut into the floor. A cuboid whose top edges carry a
    # negative (concave) rounding leaves a fillet against the floor plane, so
    # the finger follows a curve out of the bore and onto the floor instead of
    # catching on a right-angled step.
    fillet = wall_thickness / 2
    if fillet > 0:
        from pybosl2.constants import Anchor

        run = radius * 2 + fillet * 2
        dip = min(1.0, floor_thickness / 2) if floor_thickness else 0.2
        pad = cuboid(
            [run, fillet, fillet + dip],
            rounding=-fillet,
            edges=[Anchor.TOP + Anchor.FRONT, Anchor.TOP + Anchor.BACK],
            **precision_kwargs(),
        )
        x, y = _SIDE_CENTRES[side](comp_width, comp_length)
        inward = 1.0 if side in (ScoopSide.FRONT, ScoopSide.LEFT) else -1.0
        centre_z = (fillet - dip) / 2
        if side in (ScoopSide.FRONT, ScoopSide.BACK):
            placed = pad.translate([x, y + inward * fillet / 2, centre_z])
        else:
            placed = pad.rotate([0.0, 0.0, 90.0]).translate(
                [x + inward * fillet / 2, y, centre_z]
            )
        cut = cut | placed

    return cut


def build_scoop(
    comp_width: float,
    comp_length: float,
    comp_depth: float,
    side: ScoopSide,
    radius: float = 12.0,
    wall_thickness: float = 2.0,
    rounding_radius: float = DEFAULT_MOUTH_ROUNDING_MM,
    rounding_edge: float | None = None,
    floor_thickness: float | None = None,
) -> "Bosl2Solid":
    """Pick the right scoop for the compartment's depth.

    Deep compartments get a wall notch; shallow ones get the floor-blended cut,
    because a notch in a 4mm-deep well is not something a finger can use.

    Args:
        comp_width: Compartment footprint width.
        comp_length: Compartment footprint length.
        comp_depth: Compartment depth; decides which scoop is built.
        side: Which wall or edge the scoop sits on.
        radius: Scoop radius in mm.
        wall_thickness: Wall the cut passes through.
        rounding_radius: Flare at the mouth where the cut meets the rim.
        rounding_edge: Fillet where the cut emerges on a face.

    Returns:
        Bosl2Solid cutout, positioned in the compartment frame.
    """
    if comp_depth >= MIN_WALL_SCOOP_DEPTH_MM:
        return build_wall_scoop(
            comp_width, comp_length, comp_depth, side,
            radius=radius, wall_thickness=wall_thickness,
            rounding_radius=rounding_radius, rounding_edge=rounding_edge,
            floor_thickness=floor_thickness,
        )
    return build_floor_scoop(
        comp_width, comp_length, side,
        radius=radius, comp_depth=comp_depth, wall_thickness=wall_thickness,
        rounding_radius=rounding_radius, rounding_edge=rounding_edge,
        floor_thickness=floor_thickness,
    )
