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


ARC_SAMPLES = 16
"""Points per quarter-arc in the scoop profile. 16 is smooth at print scale."""

DEFAULT_BOTTOM_ROUNDING_RATIO = 0.5
"""``r2`` as a fraction of the throat half-width, when the caller names none."""

MIN_FLAT_BOTTOM_RATIO = 0.25
"""How much of the throat's half-width stays flat, however large ``r2`` is.

The base of an edge scoop is a **flat run**, not just the meeting point of two
fillets. A piece rests on it, and a finger slides along it to get under the
piece; let r2 grow to the full half-width and the flat vanishes into a U, which
is the trough shape the flat bottom exists to avoid. r2 is therefore capped so
at least this fraction of each half stays straight.
"""


def _quarter_arc(
    centre: tuple[float, float],
    radius: float,
    start_angle: float,
    end_angle: float,
    samples: int = ARC_SAMPLES,
) -> list[tuple[float, float]]:
    """Sample an arc, endpoints included.

    Args:
        centre: The arc's centre in the profile plane.
        radius: Arc radius; ``0`` collapses to the single centre point.
        start_angle: Start angle in degrees.
        end_angle: End angle in degrees.
        samples: Segments along the arc.

    Returns:
        ``[(x, y), ...]`` from start to end.
    """
    if radius <= 0:
        return [centre]
    points = []
    for index in range(samples + 1):
        angle = math.radians(
            start_angle + (end_angle - start_angle) * index / samples
        )
        points.append(
            (centre[0] + radius * math.cos(angle), centre[1] + radius * math.sin(angle))
        )
    return points


def scoop_profile(
    radius: float,
    height: float,
    top_rounding: float = DEFAULT_MOUTH_ROUNDING_MM,
    bottom_rounding: float | None = None,
) -> "Bosl2Shape2D":
    r"""Build the 2-D side profile of an **edge** scoop, in the X-Z plane.

    Two radii and three straight runs, read from the top down::

        ===========...                      ...===========   flat top surface
                     ''..                ..''                r1: rolls the top
                         \              /                    over into the wall
                          |            |                     straight throat
                          '..      ..''                      r2: wall into floor
                             ''--''                          flat bottom

    **r1** (``top_rounding``) turns the flat top surface into the scoop wall:
    the arc leaves the top face horizontally, so the surface rolls over the rim
    instead of meeting the cut at an edge, and arrives vertical at the throat.
    **r2** (``bottom_rounding``) turns the wall into the floor, leaving a flat
    bottom for a piece to sit on rather than a semicircular trough.

    Both arcs are tangent at both ends, so the whole outline is smooth without
    needing a parametric blend: the tangency is what makes it so, and two radii
    say it more directly than any curve fitted between them.

    Args:
        radius: Half-width of the straight throat — the narrowest part.
        height: Height from the floor to the rim.
        top_rounding: r1, how far the mouth rolls out at the rim. ``0`` gives a
            square-topped slot.
        bottom_rounding: r2, the fillet from the throat into the flat bottom.
            ``None`` derives it as half the throat half-width; ``0`` gives a
            square floor. Capped so part of the base stays flat whatever is
            asked for.

    Returns:
        The profile as 2-D geometry, floor at ``y=0``, rim at ``y=height``,
        centred on ``x=0``.

    Raises:
        ValueError: If ``radius`` or ``height`` is not positive, or either
            radius is negative.
    """
    from pybosl2 import shapes2d

    if radius <= 0:
        raise ValueError(f"scoop radius must be > 0; got {radius}")
    if height <= 0:
        raise ValueError(f"scoop height must be > 0; got {height}")
    if top_rounding < 0:
        raise ValueError(f"top_rounding must be >= 0; got {top_rounding}")

    if bottom_rounding is None:
        bottom_rounding = radius * DEFAULT_BOTTOM_ROUNDING_RATIO
    if bottom_rounding < 0:
        raise ValueError(f"bottom_rounding must be >= 0; got {bottom_rounding}")

    # r2 cannot eat the whole half-width: some of the base stays flat so a
    # piece has something to sit on (see MIN_FLAT_BOTTOM_RATIO). The two arcs
    # also have to share the height between them without overlapping.
    r2 = min(bottom_rounding, radius * (1.0 - MIN_FLAT_BOTTOM_RATIO))
    r1 = top_rounding
    if r1 + r2 > height:
        scale = height / (r1 + r2)
        r1, r2 = r1 * scale, r2 * scale

    # Right-hand half, walked from the centre of the floor up and outwards.
    points: list[tuple[float, float]] = [(0.0, 0.0)]
    # r2: floor into wall — centre inside the material, sweeping 270° to 360°.
    points += _quarter_arc((radius - r2, r2), r2, -90.0, 0.0)
    # The straight throat, then r1: wall into the top face, centre outside the
    # cut so the arc is concave and the top surface rolls into it.
    points.append((radius, height - r1))
    points += _quarter_arc((radius + r1, height - r1), r1, 180.0, 90.0)
    points.append((0.0, height))

    half = shapes2d.polygon([[float(x), float(y)] for x, y in points])
    return half | half.mirror([1, 0])


def floor_bore_profile(
    radius: float,
    height: float,
    top_rounding: float = DEFAULT_MOUTH_ROUNDING_MM,
) -> "Bosl2Shape2D":
    """Build the 2-D profile of a **floor** finger hole, in the X-Z plane.

    Deliberately not the edge profile. An edge scoop is a shape you sweep a
    finger *along* — flat floor, straight throat, rolled rim — while a floor
    finger hole is a bore you push a piece *up* through, so its bottom is a
    bowl tangent to the floor rather than a flat pan. Sharing one profile
    between them was convenient and produced a flat-bottomed pit where a bowl
    belongs.

    Args:
        radius: Bore radius — the widest part of the bowl.
        height: Height from the floor to the rim.
        top_rounding: How far the mouth rolls out at the rim, as ``r1`` on an
            edge scoop. ``0`` gives a square-topped bore.

    Returns:
        The profile as 2-D geometry, floor at ``y=0``, rim at ``y=height``,
        centred on ``x=0``.

    Raises:
        ValueError: If ``radius`` or ``height`` is not positive, or
            ``top_rounding`` is negative.
    """
    from pybosl2 import shapes2d

    if radius <= 0:
        raise ValueError(f"bore radius must be > 0; got {radius}")
    if height <= 0:
        raise ValueError(f"bore height must be > 0; got {height}")
    if top_rounding < 0:
        raise ValueError(f"top_rounding must be >= 0; got {top_rounding}")

    # A full circle sitting on the floor: its lower half is the bowl, tangent
    # to the floor plane, so the bottom of the cut curves into the floor.
    bore = shapes2d.circle(radius=radius, **precision_kwargs()).translate([0.0, radius])
    profile = bore

    throat_top = height - top_rounding
    if throat_top > radius:
        profile = profile | shapes2d.square(
            [radius * 2, throat_top - radius], center=True
        ).translate([0.0, radius + (throat_top - radius) / 2])

    if top_rounding > 0:
        # The same r1 roll as an edge scoop: horizontal at the top face,
        # vertical where it meets the throat.
        points = [(0.0, max(0.0, throat_top))]
        points += _quarter_arc(
            (radius + top_rounding, throat_top), top_rounding, 180.0, 90.0
        )
        points.append((0.0, height))
        mouth = shapes2d.polygon([[float(x), float(y)] for x, y in points])
        profile = profile | mouth | mouth.mirror([1, 0])

    return profile


def build_wall_scoop(
    comp_width: float,
    comp_length: float,
    comp_depth: float,
    side: ScoopSide,
    radius: float = 12.0,
    wall_thickness: float = 2.0,
    rounding_radius: float = DEFAULT_MOUTH_ROUNDING_MM,
    bottom_rounding: float | None = None,
    rounding_edge: float | None = None,
    round_inner: bool = True,
    round_outer: bool = True,
    breach_floor: bool = False,
    floor_thickness: float | None = None,
    floor_clearance: float | None = None,
) -> "Bosl2Solid":
    """Build a finger notch through a compartment wall.

    The **edge** profile from :func:`scoop_profile` — flat bottom, straight
    throat, rolled rim — swept through the wall, with a
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
        rounding_radius: ``r1`` — how far the mouth rolls out at the rim.
        bottom_rounding: ``r2`` — the fillet from the throat into the flat
            bottom. ``None`` derives it as half the throat width.
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

    profile = scoop_profile(radius, comp_depth, rounding_radius, bottom_rounding)
    return _sweep_through_wall(
        profile, comp_width, comp_length, side,
        comp_depth=comp_depth,
        wall_thickness=wall_thickness,
        rounding_radius=rounding_radius,
        rounding_edge=rounding_edge,
        round_inner=round_inner,
        round_outer=round_outer,
        breach_floor=breach_floor,
        floor_thickness=floor_thickness,
        floor_clearance=floor_clearance,
        span=span,
        radius=radius,
    )


def _sweep_through_wall(
    profile: "Bosl2Shape2D",
    comp_width: float,
    comp_length: float,
    side: ScoopSide,
    *,
    comp_depth: float,
    wall_thickness: float,
    rounding_radius: float,
    rounding_edge: float | None,
    span: float,
    radius: float,
    round_inner: bool = True,
    round_outer: bool = True,
    breach_floor: bool = False,
    floor_thickness: float | None = None,
    floor_clearance: float | None = None,
) -> "Bosl2Solid":
    """Sweep a 2-D scoop profile through a wall and place it on a side.

    Shared by the edge scoop and the floor finger hole: the *profiles* differ
    (that is the point — one is a channel, the other a bore), but everything
    around them is the same, and duplicating it is how the two drift apart.

    Args:
        profile: The scoop's 2-D side profile, floor at ``y=0``.
        comp_width: Compartment footprint width.
        comp_length: Compartment footprint length.
        side: Which wall to cut through.
        comp_depth: Compartment depth, used to size the floor clip.
        wall_thickness: The wall being crossed; sets the sweep depth.
        rounding_radius: r1, used to size the floor clip.
        rounding_edge: Face fillet; ``None`` uses half the wall.
        span: The compartment span along the cut wall.
        radius: The scoop's half-width, used to size the floor clip.
        round_inner: Fillet the compartment-side face.
        round_outer: Fillet the outward face.
        breach_floor: Skip the floor clip entirely.
        floor_thickness: Box floor, sizing the permitted dip below it.
        floor_clearance: Explicit dip below the well floor.

    Returns:
        The cutout, positioned in the compartment frame.
    """
    if rounding_edge is None:
        rounding_edge = wall_thickness / 2

    fudge = 0.03
    depth = wall_thickness + fudge
    rim = max(0.0, min(rounding_edge, (depth - 0.01) / 2))

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

    # Parts 1 and 2: the bore, swept through the wall with the same face
    # fillets an edge scoop gets. The *profile* is the floor one — a bowl
    # tangent to the floor — because this is a hole you push a piece up
    # through, not a channel you sweep a finger along.
    cut = _sweep_through_wall(
        floor_bore_profile(min(radius, span / 2), depth, rounding_radius),
        comp_width, comp_length, side,
        comp_depth=depth,
        wall_thickness=wall_thickness,
        rounding_radius=rounding_radius,
        rounding_edge=rounding_edge,
        floor_thickness=floor_thickness,
        span=span,
        radius=min(radius, span / 2),
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
