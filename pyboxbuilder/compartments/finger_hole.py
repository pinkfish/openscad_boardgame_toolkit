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
from pyboxbuilder.rounding import rounding_facets

if TYPE_CHECKING:
    from pybosl2.shapes2d import Bosl2Shape2D
    from pybosl2.shapes3d import Bosl2Solid

DEFAULT_FLOOR_DIP_MM = 0.2
"""How far a cut passes below the well floor, by default.

Its only job is to keep the cut's bottom face off the floor plane, since a
coincident face renders as speckle and is how a boolean leaves a zero-thickness
skin. 0.2mm does that. Scaling it with the floor thickness — which an earlier
version did, up to a full millimetre — spends half a 2mm floor on a cosmetic
detail, and it showed as the cut visibly eating into the floor.
"""

MIN_WALL_SCOOP_DEPTH_MM = 8.0
"""Below this a wall notch has nothing to grip, so the floor scoop is used."""

DEFAULT_MOUTH_ROUNDING_MM = 3.0
"""Fallback ``r1`` where nothing better can be derived."""

DEFAULT_TOP_ROUNDING_RATIO = 0.5
"""How far the top roll flares **outward**, as a fraction of the throat half-width.

Derived rather than fixed so the roll stays in proportion: a 3mm constant is
invisible on a 14mm finger hole and overwhelming on a 4mm one. This is the one
number that sets how *wide* the scoop's mouth is, so it is also the one to
leave alone when the width is already right.
"""

TOP_ROLL_RISE_RATIO = 1.6
"""How far the top roll reaches **down**, as a multiple of its outward flare.

The roll is an ellipse quadrant, not a circle, because its two extents answer
different questions: the flare decides how wide the mouth is, and the rise
decides how gently the top surface turns into the wall. A circle ties them
together, so the only way to get a gentler curve is a wider cut — which is
backwards on a shallow wall, where there is height to spare for the curve but
no width to spare for the mouth.
"""

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


RIM_OVERSHOOT_MM = 1.0
"""How far a scoop's outline continues above the rim.

Keeps the outline free of the zero-angle cusp that closing it flush across the
top would create, and leaves no skin at the top face. Nothing sits above the
rim, so the overshoot removes nothing that was there.
"""

ARC_SAMPLES = 16
"""Points per quarter-arc in the scoop profile. 16 is smooth at print scale."""

DEFAULT_BOTTOM_ROUNDING_RATIO = 0.65
"""``r2`` as a fraction of the throat half-width, when the caller names none.

Wider than the half it started at: the floor fillet does not change how wide
the cut is — it lives inside the throat — so it can afford a generous curve,
and a finger following the wall down wants one.
"""

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
    samples: int | None = None,
) -> list[tuple[float, float]]:
    """Sample an arc, endpoints included.

    Args:
        centre: The arc's centre in the profile plane.
        radius: Arc radius; ``0`` collapses to the single centre point.
        start_angle: Start angle in degrees.
        end_angle: End angle in degrees.
        samples: Segments along the arc. ``None`` follows the curve precision
            in force, so an export tessellates these arcs as finely as every
            other curve rather than pinning a count the caller cannot reach.

    Returns:
        ``[(x, y), ...]`` from start to end.
    """
    if radius <= 0:
        return [centre]
    if samples is None:
        from pyboxbuilder.precision import precision

        # A quarter arc gets a quarter of the facets a full circle would.
        samples = max(ARC_SAMPLES, (precision().fn or 0) // 4)
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

    flare, rise, r2 = _fit_radii(radius, height, top_rounding, bottom_rounding)

    ring = scoop_outline(radius, height, flare, r2, rise)
    return shapes2d.polygon([[float(x), float(y)] for x, y in ring])


def _fit_radii(
    radius: float,
    height: float,
    top_rounding: float,
    bottom_rounding: float | None,
) -> tuple[float, float, float]:
    """Size the two rolls to the scoop they are shaping.

    Args:
        radius: Half-width of the throat.
        height: Floor to rim.
        top_rounding: The top roll's outward flare (r1).
        bottom_rounding: Requested r2, or ``None`` to derive it.

    Returns:
        ``(flare, rise, r2)`` — how far the top roll reaches out, how far it
        reaches down, and the floor fillet.

    Only the two *vertical* extents compete for the height, so a shallow wall
    shortens the rise and leaves the flare — and therefore the width of the cut
    — alone. Scaling the flare too would narrow the mouth on exactly the boxes
    where a finger has least room to begin with.
    """
    if bottom_rounding is None:
        bottom_rounding = radius * DEFAULT_BOTTOM_ROUNDING_RATIO
    flare = max(0.0, top_rounding)
    rise = flare * TOP_ROLL_RISE_RATIO
    r2 = max(0.0, min(bottom_rounding, radius * (1.0 - MIN_FLAT_BOTTOM_RATIO)))
    if rise + r2 > height:
        scale = height / (rise + r2)
        rise, r2 = rise * scale, r2 * scale
    return flare, rise, r2


def floor_bore_outline(
    radius: float,
    height: float,
    top_rounding: float = DEFAULT_MOUTH_ROUNDING_MM,
) -> list[tuple[float, float]]:
    """The floor finger hole's closed outline, as one ring of points.

    The bore counterpart to :func:`scoop_outline`: a bowl tangent to the floor
    instead of a flat bottom, carrying the same r1 roll at its rim and the same
    overshoot above it.

    Args:
        radius: Bore radius — the widest part of the bowl.
        height: Floor to rim.
        top_rounding: r1 at the rim.

    Returns:
        ``[(x, y), ...]`` closed, floor at ``y=0``.

    Raises:
        ValueError: If ``radius`` or ``height`` is not positive, or
            ``top_rounding`` is negative.
    """
    if radius <= 0:
        raise ValueError(f"bore radius must be > 0; got {radius}")
    if height <= 0:
        raise ValueError(f"bore height must be > 0; got {height}")
    if top_rounding < 0:
        raise ValueError(f"top_rounding must be >= 0; got {top_rounding}")

    r1 = min(top_rounding, max(0.0, height - radius))
    right: list[tuple[float, float]] = []
    # The bowl: a quarter of the bore circle, from its lowest point out to the
    # side, tangent to the floor at the bottom and vertical at the side.
    right += _quarter_arc((0.0, radius), radius, -90.0, 0.0)
    right.append((radius, height - r1))
    if r1 > 0:
        right += _quarter_arc((radius + r1, height - r1), r1, 180.0, 90.0)
    right.append((radius + r1, height + RIM_OVERSHOOT_MM))

    left = [(-x, y) for x, y in reversed(right)]
    return left + right


def _elliptical_quarter(
    centre: tuple[float, float],
    flare: float,
    rise: float,
    samples: int | None = None,
) -> list[tuple[float, float]]:
    """The top roll: a quarter ellipse from the wall out to the top face.

    Vertical where it leaves the wall and horizontal where it meets the top
    face, like a quarter circle, but with the two extents settable apart so a
    shallow wall can have a gentle curve without a wide mouth.

    Args:
        centre: The ellipse's centre.
        flare: Horizontal semi-axis — how far the mouth opens out.
        rise: Vertical semi-axis — how far down the turn takes.
        samples: Segments along the arc; ``None`` follows the curve precision.

    Returns:
        ``[(x, y), ...]`` from the wall to the top face.
    """
    if flare <= 0 or rise <= 0:
        return [(centre[0], centre[1] + rise)]
    if samples is None:
        from pyboxbuilder.precision import precision

        samples = max(ARC_SAMPLES, (precision().fn or 0) // 4)
    points = []
    for index in range(samples + 1):
        angle = math.pi + (math.pi / 2) * index / samples
        points.append(
            (centre[0] + flare * math.cos(angle), centre[1] - rise * math.sin(angle))
        )
    return points


def _angle_at(centre: tuple[float, float], point: tuple[float, float]) -> float:
    """The angle, in degrees, from ``centre`` to ``point``."""
    return math.degrees(math.atan2(point[1] - centre[1], point[0] - centre[0]))


def _tangent_join(
    bottom_centre: tuple[float, float],
    bottom_radius: float,
    top_centre: tuple[float, float],
    top_radius: float,
    fallback_x: float,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Where the two arcs meet the straight run between them.

    Solved as the circles' **common tangent** rather than assumed to be the
    vertical line ``x = fallback_x``. For the usual placement the answer *is*
    that vertical — both circles are constructed tangent to it — so this
    changes no geometry today. It earns its place by not depending on that
    placement: move either centre and the profile stays tangent at both joins
    instead of stepping, which is what a step in a scoop's wall looks like.

    Args:
        bottom_centre: Centre of the r2 (floor) circle.
        bottom_radius: r2.
        top_centre: Centre of the r1 (rim) circle.
        top_radius: r1.
        fallback_x: The vertical to fall back to when no usable tangent exists
            — coincident or overlapping circles, or a degenerate radius.

    Returns:
        ``(point_on_bottom_circle, point_on_top_circle)``.
    """
    if bottom_radius <= 0 or top_radius <= 0:
        return (
            (fallback_x, bottom_centre[1]),
            (fallback_x, top_centre[1]),
        )

    from pybosl2 import geometry

    try:
        tangents = geometry.circle_circle_tangents(
            radius1=bottom_radius, center1=list(bottom_centre),
            radius2=top_radius, center2=list(top_centre),
        )
    except Exception:
        tangents = []

    # The wanted tangent is an **internal** one. The cut's boundary wraps
    # around the *outside* of the floor circle and the *inside* of the rim
    # circle — the two arcs curve opposite ways — so the run touches the floor
    # circle on its right and the rim circle on its left, and the external
    # tangents (which touch both on the same side) belong to a different shape
    # entirely. Filtering for "outside both" picked one of those and threw the
    # profile 12mm wide.
    best = None
    for low, high in tangents:
        low_pt = (float(low[0]), float(low[1]))
        high_pt = (float(high[0]), float(high[1]))
        if high_pt[1] <= low_pt[1]:
            continue  # runs downward: that is the mirrored half's tangent
        if low_pt[0] < bottom_centre[0] - 1e-9:
            continue  # touches the floor circle on its buried side
        if high_pt[0] > top_centre[0] + 1e-9:
            continue  # touches the rim circle on its buried side
        skew = abs(high_pt[0] - low_pt[0])
        if best is None or skew < best[0]:
            best = (skew, low_pt, high_pt)

    if best is None:
        return (
            (fallback_x, bottom_centre[1]),
            (fallback_x, top_centre[1]),
        )
    return best[1], best[2]


def scoop_outline(
    radius: float,
    height: float,
    top_rounding: float,
    bottom_rounding: float,
    top_rise: float | None = None,
) -> list[tuple[float, float]]:
    """The edge scoop's closed outline, as one ring of points.

    Returned as a point ring rather than as 2-D geometry because the ring is
    what an offset sweep needs: it follows the outline around, so the fillet it
    lays on each face traces the scoop's own curve. A shape built by unioning
    two mirrored halves loses that — it is the same region, but the boundary
    has to be recovered from it, and anything that recovers it convexly (a
    hull, say) bridges straight across the notch.

    Args:
        radius: Half-width of the straight throat.
        height: Floor to rim.
        top_rounding: How far the top roll flares outward, already capped.
        bottom_rounding: r2, already capped to fit.
        top_rise: How far the top roll reaches down. ``None`` makes it equal to
            the flare, i.e. a circular quarter-roll.

    Returns:
        ``[(x, y), ...]`` closed counter-clockwise, floor at ``y=0``.
    """
    flare, r2 = top_rounding, bottom_rounding
    rise = flare if top_rise is None else top_rise
    bottom_centre = (radius - r2, r2)
    top_centre = (radius + flare, height - rise)
    join_low, join_high = _tangent_join(
        bottom_centre, r2, top_centre, flare, radius
    )

    right: list[tuple[float, float]] = []
    # r2 rolls the floor into the wall, a straight run carries up, and the top
    # roll turns the wall into the top face. The straight run is the two
    # circles' **common tangent**, so both joins are tangent by construction
    # rather than by assuming the run is vertical.
    right += _quarter_arc(bottom_centre, r2, -90.0, _angle_at(bottom_centre, join_low))
    right.append((radius, height - rise))
    right += _elliptical_quarter(top_centre, flare, rise)
    # Carry on straight up past the rim. Closing the ring along the top instead
    # would put a **cusp** at each end of the r1 arc: the arc arrives there
    # travelling horizontally outward and the closing edge leaves horizontally
    # back inward, so the outline doubles on itself at zero angle. Offsetting
    # such a corner miters to infinity — measured, a ±15mm profile came back
    # ±55mm. There is no material above the rim, so the overshoot costs nothing
    # and it also guarantees the cut leaves no skin at the top face.
    right.append((radius + flare, height + RIM_OVERSHOOT_MM))

    left = [(-x, y) for x, y in reversed(right)]
    return left + right


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
    rounding_radius: float | None = None,
    bottom_rounding: float | None = None,
    rounding_edge: float | None = None,
    round_inner: bool = True,
    round_outer: bool = True,
    breach_floor: bool = False,
    floor_thickness: float | None = None,
    floor_clearance: float | None = None,
    top_limit: float | None = None,
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
            ``None`` derives it as half the throat half-width, so the roll
            stays in proportion to the scoop.
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
    if rounding_radius is None:
        rounding_radius = radius * DEFAULT_TOP_ROUNDING_RATIO
    if wall_thickness <= 0:
        raise ValueError(f"wall_thickness must be > 0; got {wall_thickness}")

    span = comp_width if side in (ScoopSide.FRONT, ScoopSide.BACK) else comp_length

    # The mouth is `radius + r1` wide on each side, and the two have to share
    # the span. Capping the throat first and giving r1 whatever is left sounds
    # equivalent and is not: a throat already at half the span leaves r1 exactly
    # zero, which silently deletes the top roll — the most visible part of the
    # scoop — on every narrow compartment. Shrink them together instead, so a
    # tight span costs both a little rather than costing r1 everything.
    if radius + rounding_radius > span / 2:
        scale = (span / 2) / (radius + rounding_radius)
        radius, rounding_radius = radius * scale, rounding_radius * scale
    rounding_radius = max(0.0, rounding_radius)

    if rounding_edge is None:
        rounding_edge = wall_thickness / 2

    # Just the wall, plus a hair at each face so the boolean has no coincident
    # plane to resolve. See the note above on why this must not be larger.
    fudge = 0.03
    depth = wall_thickness + fudge
    rim = max(0.0, min(rounding_edge, (depth - 0.01) / 2))

    # Named rather than splatted: `_fit_radii` returns (flare, rise, r2) and
    # `scoop_outline` takes (top_rounding, bottom_rounding, top_rise), so
    # `*_fit_radii(...)` fed the top roll's **rise** to the floor fillet and the
    # floor fillet to the rise. The bottom curve was therefore sized off the
    # rounding radius (1.6x the top flare) instead of off the throat radius —
    # both curves of the U driven by the same number, which is exactly what it
    # looked like. `scoop_profile` had the order right all along.
    flare, rise, r2 = _fit_radii(
        radius, comp_depth, rounding_radius, bottom_rounding
    )
    outline = scoop_outline(radius, comp_depth, flare, r2, rise)
    return _sweep_through_wall(
        outline, comp_width, comp_length, side,
        comp_depth=comp_depth,
        wall_thickness=wall_thickness,
        rounding_radius=rounding_radius,
        rounding_edge=rounding_edge,
        round_inner=round_inner,
        round_outer=round_outer,
        breach_floor=breach_floor,
        floor_thickness=floor_thickness,
        floor_clearance=floor_clearance,
        top_limit=top_limit,
        span=span,
        radius=radius,
    )


def _roundover_profile(radius: float, steps: int):
    """A rim profile that **rounds the face over** into the cut.

    ``os_circle`` is the obvious choice and is the wrong shape: its arc is
    tangent to the cut's wall and meets the end face at 90°, which on a
    subtractive solid hollows a cove *inside* the wall and leaves the opening
    at nominal size — a cutout, not a roundover.

    The roundover is the mirrored arc, tangent to the **face**::

        z     = r · (1 - cos a)      # depth from the face
        inset = r · sin a            # how far the cut has narrowed

    so at the face the cut is a full ``r`` wider (and tangent to the face, so
    the face flows into it), and by depth ``r`` it has settled onto the wall.

    Args:
        radius: The fillet radius.
        steps: Points along the arc.

    Returns:
        An ``OSProfile`` for :meth:`Path2D.offset_sweep`, whose ``x`` is the
        inward offset and ``y`` the depth from the face.
    """
    from pybosl2.skin import os_profile

    points = []
    for index in range(steps + 1):
        angle = (math.pi / 2) * index / steps
        points.append([radius * math.sin(angle), radius * (1.0 - math.cos(angle))])
    return os_profile(points)


def _sweep_through_wall(
    outline: list,
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
    top_limit: float | None = None,
) -> "Bosl2Solid":
    """Sweep a 2-D scoop profile through a wall and place it on a side.

    Shared by the edge scoop and the floor finger hole: the *profiles* differ
    (that is the point — one is a channel, the other a bore), but everything
    around them is the same, and duplicating it is how the two drift apart.

    Args:
        outline: The scoop's closed 2-D outline as a point ring, floor at
            ``y=0``. A ring rather than a 2-D shape because the fillet has to
            follow it around: the sweep offsets the outline itself, so the
            fillet traces the scoop's own curve on each face.
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
        top_limit: Height, in the scoop's own frame, above which the cut is
            trimmed away. Needed when there is material above the cut — the
            lid band of a lidded box — where the outline's rim overshoot would
            otherwise carry the cut straight through it. ``None`` (a free rim)
            keeps the overshoot, which is what leaves no skin at the top face.

    Returns:
        The cutout, positioned in the compartment frame.
    """
    if rounding_edge is None:
        rounding_edge = wall_thickness / 2

    fudge = 0.03
    depth = wall_thickness + fudge
    rim = max(0.0, min(rounding_edge, (depth - 0.01) / 2))

    # BOSL2's own offset_sweep, which lofts between offsets of the outline, so
    # the fillet follows the cut's curve. (A hand-rolled stand-in chained
    # convex hulls between slices, and a hull across a U-shaped outline bridges
    # the notch — the fillet came out as a ramp across the opening.)
    from pybosl2.path2d import Path2D

    steps = max(8, rounding_facets()["fn"] // 4)
    ring = [[float(x), float(y)] for x, y in outline]
    fillet = rim if (rim > 0 and (round_outer or round_inner)) else 0.0

    if fillet > 0:
        # The path is the cross-section **at the end face**, and a rim profile
        # moves it as you travel inward. So the widened outline is the path and
        # the rim brings it back in: that is what puts the extra material at
        # the face, where the roundover belongs.
        path = Path2D(ring, closed=True).offset(delta=fillet)
        swept = path.offset_sweep(
            height=depth,
            bottom=_roundover_profile(fillet, steps) if round_outer else None,
            top=_roundover_profile(fillet, steps) if round_inner else None,
            steps=steps,
        )
    else:
        swept = Path2D(ring, closed=True).offset_sweep(height=depth, steps=steps)
    # offset_sweep hands back a VNF; realise it and wrap the native solid so
    # the transforms and booleans below have something to work with.
    from pybosl2.shapes3d.base import CsgSolid

    swept = CsgSolid(swept.polyhedron())

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

        dip = floor_clearance if floor_clearance is not None else min(
            DEFAULT_FLOOR_DIP_MM,
            (floor_thickness / 4) if floor_thickness else DEFAULT_FLOOR_DIP_MM,
        )
        dip = max(0.0, dip)
        reach = comp_depth + rounding_radius + rim + 1.0
        keep = cuboid([span * 2 + radius * 4, depth * 4, reach * 2]).translate(
            [0.0, 0.0, reach - dip]
        )
        standing = standing & keep

    if top_limit is not None:
        from pybosl2 import cuboid

        reach = comp_depth + rounding_radius + rim + RIM_OVERSHOOT_MM + 1.0
        standing = standing & cuboid(
            [span * 2 + radius * 4, depth * 4, reach * 2]
        ).translate([0.0, 0.0, top_limit - reach])

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
    rounding_radius: float | None = None,
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
    if rounding_radius is None:
        rounding_radius = radius * DEFAULT_TOP_ROUNDING_RATIO
    depth = comp_depth if comp_depth and comp_depth > 0 else radius

    # Parts 1 and 2: the bore, swept through the wall with the same face
    # fillets an edge scoop gets. The *profile* is the floor one — a bowl
    # tangent to the floor — because this is a hole you push a piece up
    # through, not a channel you sweep a finger along.
    cut = _sweep_through_wall(
        floor_bore_outline(min(radius, span / 2), depth, rounding_radius),
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
    rounding_radius: float | None = None,
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
        rounding_radius: ``r1``; ``None`` derives it from the throat width.
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
