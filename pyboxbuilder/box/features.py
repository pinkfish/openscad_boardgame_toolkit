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

_COINCIDENT_EPS_MM = 0.02
"""How far a cutting solid is backed off a face it would otherwise touch exactly.

Coincident surfaces are the one case CSG cannot decide: the difference keeps a
zero-width sliver and the face survives, so a cut that is geometrically correct
measures as if it never ran.
"""

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
    # The original's CapBoxDefaultCapHeight / CapBoxDefaultLidWallThickness,
    # then capped so the corner finger cutout below it still has somewhere to
    # go. Half the height is a fine skirt on a tall box and swallows a short one
    # whole: at 11mm it would take 5.5, leaving 5.5 for a cut that needs 4 and a
    # 2mm foot. The floor is the lid plate plus the shortest usable skirt, so
    # the smallest cap box is exactly `lid + 3 + 4 + 2` (FR-002n).
    cap_h = spec.get("cap_height")
    if cap_h is None:
        room = spec["height"] - CAP_FINGER_CURVE_TOTAL_MM - CAP_FINGER_FOOT_MM
        cap_h = min(
            min(10.0, spec["height"] / 2),
            max(lt + CAP_FINGER_MIN_SKIRT_MM, room),
        )
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


CAP_FINGER_MIN_RADIUS_MM = 2.0
"""Smallest either profile radius may be on a cap box's corner cutout (FR-002k).

The **pair** is the budget: 2mm rolling in at the top and 2mm rolling out at the
bottom, :data:`CAP_FINGER_CURVE_TOTAL_MM` between them.
"""

CAP_FINGER_CURVE_TOTAL_MM = 2 * CAP_FINGER_MIN_RADIUS_MM
"""Height the two rolls need between them, with no straight run at all (FR-002k).

This is what sets the smallest cap box that can be built: a lid thickness, this,
and a foot. Sized as a total rather than per-radius because it is the total that
competes with the box's height — a 4mm budget fits boxes an 8mm one refuses.
"""

CAP_FINGER_FOOT_MM = 2.0
"""Full-thickness body left below the cutout (FR-002l).

The cut is a recess in the side, not a through-slot; the corner it is cut into
is the corner the box is stacked and dropped on.
"""

CAP_FINGER_MIN_SKIRT_MM = 3.0
"""Shortest skirt a cap lid may have when the body is cut for finger holds.

The skirt has to grip *something* at the corner being pushed at. Below 3mm there
is not enough of it to hold the lid square, and the lid rocks off that corner
rather than lifting.
"""

CAP_FINGER_MIN_LENGTH_MM = 10.0
"""Shortest run along each side — a fingertip's width (FR-002m)."""

CAP_FINGER_MAX_LENGTH_SHARE = 1 / 6
"""Longest run along each side, as a share of it (FR-002m).

Two cutouts per side then leave two thirds of the band for the skirt to grip.
"""


@dataclass(frozen=True)
class CapFingerMetrics:
    """The numbers a cap box's four corner cutouts are cut from."""

    length_x: float
    """How far each cutout runs along the width."""
    length_y: float
    """How far each cutout runs along the length."""
    height: float
    """How far down from the skirt the cut reaches."""
    radius: float
    """Both profile radii — the first and second roll."""
    base_z: float
    """Where the cut bottoms out. A foot of body survives below it."""


def cap_finger_metrics(spec: dict) -> CapFingerMetrics:
    """Size a cap box's corner finger cutouts, or explain why it cannot have any.

    Args:
        spec: Needs `width`, `length`, `height`; reads `floor_thickness` and
            optionally `cap_finger_length`, `cap_finger_height` and
            `cap_finger_radius`.

    Returns:
        The cutout geometry (FR-002i–FR-002m).

    Raises:
        ValueError: If the box cannot stack a lid, a 3mm skirt, both rolls and
            the foot (FR-002n) — the smallest cap box is
            ``lid + 3 + 4 + 2``. A cap box built without the cutouts has no way
            to be opened, so this refuses rather than shrinking them.
    """
    m = cap_metrics(spec)
    lt = spec.get("lid_thickness", 2.0)

    radius = spec.get("cap_finger_radius")
    if radius is None:
        radius = CAP_FINGER_MIN_RADIUS_MM
    radius = max(radius, CAP_FINGER_MIN_RADIUS_MM)

    # Read down the box: the lid plate, then the skirt it grips by, then the two
    # rolls, then the foot. That stack is the smallest cap box there can be.
    curves = max(2 * radius, CAP_FINGER_CURVE_TOTAL_MM)
    minimum = lt + CAP_FINGER_MIN_SKIRT_MM + curves + CAP_FINGER_FOOT_MM
    # The cut hangs below the skirt, so what it has to spend is everything from
    # there down to the foot.
    available = m.band_z - CAP_FINGER_FOOT_MM
    if m.cap_height - lt < CAP_FINGER_MIN_SKIRT_MM or available < curves - 1e-9:
        raise ValueError(
            f"cap box {spec.get('label', '')!r} is {spec['height']:.1f}mm tall "
            f"and cannot carry a corner finger cutout: it needs at least "
            f"{minimum:.1f}mm — a {lt:.1f}mm lid, a "
            f"{CAP_FINGER_MIN_SKIRT_MM:.1f}mm skirt, {curves:.1f}mm of curve "
            f"(two {radius:.1f}mm rolls) and a {CAP_FINGER_FOOT_MM:.1f}mm foot "
            f"— and has a {m.cap_height:.1f}mm skirt with {available:.1f}mm "
            f"below it. Use a slipover box at this size: its corner notches "
            f"open a shallow box that a cap lid cannot."
        )

    height = spec.get("cap_finger_height")
    if height is None:
        height = curves
    height = min(max(height, curves), available)

    def _run(dimension: float) -> float:
        # A sixth of the side, but never less than a fingertip: 10mm is what a
        # finger needs, a sixth is what the skirt would prefer.
        return max(
            CAP_FINGER_MIN_LENGTH_MM, dimension * CAP_FINGER_MAX_LENGTH_SHARE
        )

    override = spec.get("cap_finger_length")
    return CapFingerMetrics(
        length_x=override if override is not None else _run(spec["width"]),
        length_y=override if override is not None else _run(spec["length"]),
        height=height,
        radius=radius,
        base_z=m.band_z - height,
    )


def cap_finger_cutouts(spec: dict) -> "Bosl2Solid":
    """The four corner cutouts that let a cap lid be pushed off (FR-002i).

    Two wall scoops meeting at each corner — the same :func:`corner_catch` a
    slipover sleeve uses, and the original toolkit's ``CornerCatch`` before
    that — so the cut arrives with the roll and the fillets already right.

    Corners rather than side-centres: a finger pushing up in a corner recess
    loads the skirt along **both** adjoining faces at once, so the lid lifts
    square instead of cocking, and the bearing stays in the middle of each wall
    where there is material behind it.

    Args:
        spec: As :func:`cap_finger_metrics`.

    Returns:
        The solid to subtract from the body.

    Raises:
        ValueError: Via :func:`cap_finger_metrics`, when the box is too short.
    """
    from pyboxbuilder.compartments.element import union_all

    m = cap_metrics(spec)
    f = cap_finger_metrics(spec)
    width, length = spec["width"], spec["length"]

    parts = []
    for at, towards, run in (
        ((0.0, 0.0), (1, 1), (f.length_x, f.length_y)),
        ((width, 0.0), (-1, 1), (f.length_x, f.length_y)),
        ((0.0, length), (1, -1), (f.length_x, f.length_y)),
        ((width, length), (-1, -1), (f.length_x, f.length_y)),
    ):
        # `corner_catch` takes one half-width for both arms, so the shorter run
        # governs: a cutout that overran its own side would eat into the next
        # corner's.
        # `corner_catch` centres each arm's sweep **on** the wall it is given,
        # so at a box corner half of it lies outside the box. What is wanted
        # here is the body's outer skin — the same step the band above is inset
        # by — so each corner's cutter moves inward by half that skin.
        parts.append(
            corner_catch(
                at, towards,
                radius=min(run),
                height=f.height,
                wall_thickness=m.inset,
                rounding_edge=m.inset / 2,
                top_rounding=f.radius,
                bottom_rounding=f.radius,
            ).translate([
                towards[0] * m.inset / 2, towards[1] * m.inset / 2, f.base_z,
            ])
        )
    cutouts = union_all(parts)
    assert cutouts is not None, "four corners always produce a solid"
    return cutouts


def cap_body(spec: dict) -> "Bosl2Solid":
    """A cap box's body: full footprint below, stepped in for the skirt above."""
    from pyboxbuilder.box.shell import block, build_shell

    m = cap_metrics(spec)
    # `interior_top`: the body is already shortened for the cap, so its own top
    # is the top of the inside — subtracting a lid thickness again would push
    # every finger hole a lid deeper than it belongs.
    shell = build_shell({
        **spec, "height": m.body_height, "interior_top": m.body_height,
    })
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
    body = shell & keep
    # Somewhere to push the lid off from. Without this a cap box is a smooth
    # friction fit with no purchase but the seam (FR-002i).
    if spec.get("cap_finger_cutouts", True):
        body = body - cap_finger_cutouts(spec)
    return body


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


SLIPOVER_SLEEVE_WALL_SHARE = 0.5
"""How thick the sleeve's wall is, as a share of the box's wall (FR-002o).

A **half** wall. The sleeve is a skin over a box that already has a full wall
behind it everywhere the sleeve touches, so a full-thickness sleeve is a second
wall carrying nothing — it costs the interior two full walls of width across
every axis, and prints a part twice as heavy as the job needs. The same
reasoning the cap box's skirt already uses.
"""


def slipover_metrics(spec: dict) -> tuple[float, float]:
    """(inset per side, body height) for a slipover box.

    The sleeve's outer face is the declared footprint, so the body is set in by
    the sleeve's own wall thickness all round — **half** the box's wall
    (FR-002o) — and stops a lid thickness short.

    Args:
        spec: Needs `height`; reads `wall_thickness`, `lid_thickness` and
            `size_spacing`.

    Returns:
        ``(inset per side, body height)``.
    """
    wt = spec.get("wall_thickness", 2.0)
    lt = spec.get("lid_thickness", 2.0)
    wiggle = spec.get("size_spacing", WIGGLE_MM)
    return wt * SLIPOVER_SLEEVE_WALL_SHARE + wiggle, spec["height"] - lt - wiggle


@dataclass(frozen=True)
class Closure:
    """The two halves of a closure feature.

    `body` is cut from or added to the box; `lid` likewise for the lid. Which
    of the two applies is the caller's business — a rabbet subtracts its body
    half and adds its lid half, a knuckle adds both.
    """

    body: "Bosl2Solid | None" = None
    lid: "Bosl2Solid | None" = None
    body_cut: "Bosl2Solid | None" = None
    """Volume the **body** must give up for the lid's half to move."""
    lid_cut: "Bosl2Solid | None" = None
    """Volume the **lid** must give up for the body's half.

    Both directions are needed once a hinge sits inside the box: each half's
    knuckles then stand in space the other half would otherwise fill. Relieving
    only one side leaves the two fused just as surely as relieving neither.
    """


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


def sliding_dovetail(spec: dict) -> tuple[float, float]:
    """The dovetail depths that hold a sliding lid in its grooves.

    The lid's two long edges are angled — a dovetail — so the lid is trapped in
    its grooves. In cross-section, perpendicular to the slide axis, the lid is a
    trapezoid whose **top** face is the box interior (no key — the top sits
    flush with the inner walls) and whose **bottom** face reaches **half** the
    wall width into each wall. The groove never reaches the outer face, so
    there is always wall material behind it to support the lid (FR-002c).

    Args:
        spec: Reads `wall_thickness`.

    Returns:
        ``(top, bottom)`` — how far the key reaches into each side wall at the
        lid's top face and at its underside, in mm. The top is ``0`` (the lid's
        top face is the interior width); the bottom is half the wall width.
    """
    wt = spec.get("wall_thickness", 2.0)
    return 0.0, wt / 2


def lead_chamfer_size(spec: dict) -> float:
    """The slight chamfer that lets a lid start into its grooves (FR-002d).

    A **quarter** of the lid's thickness. It was half, which on a 2mm lid takes
    the leading end down to a 1mm knife edge — enough of a taper to read as a
    wedge, which is the shape a sliding lid should not have anywhere. A quarter
    still keeps the lip off the groove floor while the leading face stays
    recognisably a face.

    Args:
        spec: Reads `lid_thickness`; an explicit `lead_chamfer` wins.

    Returns:
        The chamfer depth in mm.
    """
    lt = spec.get("lid_thickness", 2.0)
    return spec.get("lead_chamfer", lt / 4)


def lid_corner_rounding(spec: dict) -> float:
    """The radius on the sliding lid's leading corners (FR-002e4).

    Args:
        spec: Reads `wall_thickness`; an explicit `lid_corner_rounding` wins.

    Returns:
        The radius in mm — a quarter of the wall by default, capped at the
        dovetail's depth so the rounding cannot eat the key that retains the
        lid.
    """
    wt = spec.get("wall_thickness", 2.0)
    _, bottom_key = sliding_dovetail(spec)
    radius = spec.get("lid_corner_rounding")
    if radius is None:
        radius = wt / 4
    return max(0.0, min(radius, bottom_key))


def _dovetail_solid(
    along_axis: str,
    bottom_along: tuple[float, float],
    top_along: tuple[float, float],
    across_center: float,
    bottom_across: float,
    top_across: float,
    height: float,
    z0: float,
    corner_rounding: float = 0.0,
) -> "Bosl2Solid":
    """A prism dovetailed on its two flanks and, at the closed end, in depth.

    Both faces are rectangles given by their **along**-axis span and their
    **across**-axis width. The across width tapers between them — that is the
    dovetail on the two side walls. The along span may also differ, and when it
    does the difference is all at the *closed* end: the bottom face reaches
    further under the stop wall than the top face does, which is the back seat
    the lid's leading end slides into (FR-002e). The open end is the same at
    both faces, so the lid finishes flush with the mouth.

    ``corner_rounding`` rounds all four vertical corners, so the pair that goes
    in first does not snag on the groove mouths (FR-002e4).

    The rounding is uniform rather than per-corner because pybosl2 0.7.8's
    per-corner ``rounding`` list **translates the whole solid**: a lid asked for
    ``[0, 0, r, r]`` came out 23mm down the slide axis, its leading end 23mm
    inside the box and its trailing end hanging that far outside. A scalar (or
    four equal values) is correct. Rounding all four is no loss anyway — the
    trailing pair is the exposed end, which the box type rounds again anyway.
    """
    from pybosl2.shapes3d import prismoid

    bottom_size = bottom_along[1] - bottom_along[0]
    top_size = top_along[1] - top_along[0]
    bottom_center = (bottom_along[0] + bottom_along[1]) / 2
    shift_along = (top_along[0] + top_along[1]) / 2 - bottom_center

    if along_axis == "x":
        solid = prismoid(
            [bottom_size, bottom_across],
            [top_size, top_across],
            height=height,
            shift=[shift_along, 0.0],
            rounding=corner_rounding,
            **precision_kwargs(),
        )
        return solid.translate([bottom_center, across_center, z0])
    solid = prismoid(
        [bottom_across, bottom_size],
        [top_across, top_size],
        height=height,
        shift=[0.0, shift_along],
        rounding=corner_rounding,
        **precision_kwargs(),
    )
    return solid.translate([across_center, bottom_center, z0])


def _lead_chamfer(
    along_axis: str,
    lead: float,
    across_min: float,
    across_max: float,
    z_base: float,
    size: float,
    from_top: bool = False,
    face_slope: float = 0.0,
) -> "Bosl2Solid":
    """A 45° wedge beveling one of the lid's leading horizontal edges.

    ``lead`` is the leading end's coordinate along the slide axis at the face
    being cut — the end that enters the box first. The wedge is ``size`` deep at
    that face and tapers to nothing ``size`` away from it, across the lid's full
    width, so the lid starts into the grooves instead of catching on their
    mouths.

    Args:
        along_axis: ``"x"`` or ``"y"`` — the slide axis.
        lead: The leading face's coordinate along that axis, at ``z_base``.
        across_min: Low edge of the span to cut, across the slide axis.
        across_max: High edge of that span.
        z_base: The face to cut from — the lid's underside, or its top face
            when ``from_top``.
        size: The chamfer's depth.
        from_top: Cut the leading **top** edge instead of the bottom one. The
            underside chamfer keeps the thin leading lip off the groove floor;
            the top one keeps the lid's top corner off the wall lip at the
            mouth. Between them the leading end is eased both ways.
        face_slope: How far the leading face advances along the slide axis per
            unit of height — the back seat's taper. Only the ``from_top`` cut
            needs it: that wedge's inner vertex has to sit **on** the sloped
            face, because the face leans away from a vertical cut going down,
            so a vertical one leaves a feather edge hanging off the face
            instead of taking the corner off it. The underside cut leans the
            other way and is already behind the face at every height.

    Returns:
        The wedge to subtract from the lid.
    """
    from pybosl2.shapes3d import prismoid

    span = across_max - across_min
    across_center = (across_min + across_max) / 2
    # The full-width face is at `z_base` and the wedge shrinks to a line `size`
    # away from it, so the prismoid's tapering end is whichever face is inside.
    lower, upper = ([0.0, size] if from_top else [size, 0.0])
    shift = (size / 2 + size * face_slope) if from_top else -size / 2
    z0 = z_base - size if from_top else z_base
    offset = (-size * face_slope) if from_top else size / 2
    # Riding the sloped face exactly makes the cutter's near surface *coincident*
    # with it, and a coincident subtraction leaves a zero-width sliver that keeps
    # the original face in the mesh — the cut measured as if it had never
    # happened. Backing the whole wedge off by a hair puts it clearly outside the
    # solid, at the cost of that hair off the chamfer.
    offset -= _COINCIDENT_EPS_MM
    if along_axis == "x":
        solid = prismoid(
            [lower, span], [upper, span], height=size, shift=[shift, 0.0],
            **precision_kwargs(),
        )
        return solid.translate([lead + offset, across_center, z0])
    solid = prismoid(
        [span, lower], [span, upper], height=size, shift=[0.0, shift],
        **precision_kwargs(),
    )
    return solid.translate([across_center, lead + offset, z0])


def dovetail_track(spec: dict, along_axis: str = "x") -> Closure:
    """The dovetailed channel a lid slides in, and the lid that fills it.

    One slot does both halves of the job, because they are the same slot: it
    leaves the interior clear at the top and bites half the wall width into
    each side wall at the bottom, to make the dovetail grooves, and it runs out
    through the far end wall so the lid has somewhere to enter. The groove is
    therefore wider at its floor than at its opening, which is what traps the
    lid: it can be slid along the axis but never lifted straight out. The
    groove never reaches the outer face — half the wall always remains behind
    it — so the walls still support the lid. Cutting only the grooves leaves a
    box with a solid wall across the front of its own track — a lid that can be
    dropped in but never slid.

    **The stop wall carries a dovetail too** (FR-002e), cut to the same depth as
    the sides: full thickness at the channel opening, half of it at the channel
    floor. That is a *seat*, not a catch. The lid's leading end is tapered to
    match, so the two faces stay parallel with the slide clearance between them
    for the whole travel — the lid slides in freely and lands in the seat — but
    once home, lifting the back of the lid drives its leading lip straight into
    the stop wall. Without it the leading end rests on nothing and the lid sits
    proud at the back.

    What must *not* be here is a **wedge catch**: a taper the lid has to be
    forced past to close and sprung back out to open. Nothing in this geometry
    interferes at any point in the travel, which is the property to check — a
    matched taper and a wedge look alike in a render and differ entirely in
    the hand. Holding the closed lid shut is :func:`sliding_catch`'s job, and
    that is a bump and dimple.

    The lid is the matching solid, cut short by `sliding_slack` on every mating
    face so it slides freely, with its two leading corners rounded and its
    leading edges chamfered so it starts into the grooves rather than snagging
    on their mouths (FR-002c, FR-002d, FR-002e4). The lid fills the channel
    flush with the open end.

    Args:
        spec: Needs `width`, `length`, `height`; reads `wall_thickness`,
            `lid_thickness`, and optionally `lead_chamfer`,
            `lid_corner_rounding` and `sliding_slack` (per-side clearance,
            default 0.1mm).
        along_axis: ``"x"`` to slide along the width, ``"y"`` along the length.

    Returns:
        The channel to subtract from the body, and the lid that fills it.
    """
    wt = spec.get("wall_thickness", 2.0)
    lt = spec.get("lid_thickness", 2.0)
    s = spec.get("sliding_slack", 0.1)
    chamfer = lead_chamfer_size(spec)
    corner_rounding = lid_corner_rounding(spec)
    top_key, bottom_key = sliding_dovetail(spec)

    if along_axis == "x":
        along = spec["width"]
        across = spec["length"]
    else:
        along = spec["length"]
        across = spec["width"]

    z0 = spec["height"] - lt
    interior_across = across - 2 * wt

    # The lid runs from under the stop wall out to the open face, so the closed
    # box is flush. Its top face is the interior (no key) and its underside
    # reaches `bottom_key` into each wall and under the stop wall, cut short by
    # the clearance on every mating face. The leading end's taper matches the
    # back seat's, so the two faces stay `s` apart for the whole travel.
    lid = _dovetail_solid(
        along_axis,
        (wt - bottom_key + s, along),
        (wt - top_key + s, along),
        across / 2,
        interior_across + 2 * bottom_key - 2 * s,
        interior_across + 2 * top_key - 2 * s,
        lt,
        z0,
        corner_rounding=corner_rounding,
    )

    # The channel: the same solid, larger by the clearance and a hair. Its floor
    # reaches `bottom_key` into each wall and into the stop wall, its opening
    # `top_key`, and it runs out through the open end wall. Its corners stay
    # square — the rounding is the lid's clearance, not a shape they share.
    channel = _dovetail_solid(
        along_axis,
        (wt - bottom_key - 0.05, along + 0.05),
        (wt - top_key - 0.05, along + 0.05),
        across / 2,
        interior_across + 2 * bottom_key + 0.1,
        interior_across + 2 * top_key + 0.1,
        lt + 0.1,
        z0 - 0.05,
    )

    # Chamfers on the leading end's two horizontal edges ease the lid in: the
    # underside one keeps the thin leading lip off the groove floor, the top one
    # keeps the lid's top corner off the wall lip at the mouth.
    if chamfer > 0:
        flank_min = wt - bottom_key + s
        flank_max = across - wt + bottom_key - s
        lid = lid - _lead_chamfer(
            along_axis, wt - bottom_key + s, flank_min, flank_max, z0, chamfer
        )
        lid = lid - _lead_chamfer(
            along_axis, wt - top_key + s, flank_min, flank_max, z0 + lt,
            chamfer, from_top=True,
            face_slope=(bottom_key - top_key) / lt if lt else 0.0,
        )

    return Closure(body=channel, lid=lid)


def sliding_track(spec: dict) -> Closure:
    """The sliding channel and lid, in the slide-along-X frame.

    A thin wrapper over :func:`dovetail_track` for the types that always slide
    along X (``SlidingCatchBox``, ``CardLibraryBox``).
    """
    return dovetail_track(spec, "x")


def sliding_catch(
    spec: dict, radius: float = 1.0, along_axis: str = "x"
) -> Closure:
    """A bump-and-dimple detent that clicks the sliding lid shut (FR-002e1).

    A pair of bumps on the lid drop into matching dimples in the two groove
    walls. The dimple is cut a touch larger so the two are not an interference
    fit — the lid should click, not jam. This is the *only* catch a sliding box
    gets: a wedge at the stop end would close by driving the lid's thinnest
    section under an overhang, whereas a bump deflects by its own height, across
    the lid's thickness (see :func:`dovetail_track`).

    **The catch sits at the outlet**, the mouth the lid enters and leaves by, so
    it engages in the last few millimetres of travel (FR-002e2). At the closed
    end instead, the bump would be dragged the whole length of the groove on
    every open and close — wearing the groove, making a long lid stiff to start,
    and telling the hand nothing about when the lid is home.

    Args:
        spec: Needs `width`, `length`, `height`; reads `wall_thickness` and
            `lid_thickness`.
        radius: The bump's radius. The dimple is half a fit clearance larger.
        along_axis: ``"x"`` to slide along the width, ``"y"`` along the length —
            the same frame :func:`dovetail_track` was given, so the catch lands
            on the two walls that actually carry the grooves.

    Returns:
        The dimples to subtract from the body, and the bumps to add to the lid.
    """
    from pybosl2 import sphere

    from pyboxbuilder.box.shell import block

    wt = spec.get("wall_thickness", 2.0)
    lt = spec.get("lid_thickness", 2.0)
    s = spec.get("sliding_slack", 0.1)
    _, bottom_key = sliding_dovetail(spec)

    along = spec["width"] if along_axis == "x" else spec["length"]
    across = spec["length"] if along_axis == "x" else spec["width"]

    # Just inside the outlet face, and on the lid's dovetail flank at
    # mid-thickness — which is where the lid's own material is. Centring on the
    # wall's inner face instead leaves the bump hanging beside the lid rather
    # than on it, because the flank has already leaned in by then.
    at_along = along - wt - 2 * radius
    flank = wt - bottom_key / 2 + s
    z = spec["height"] - lt / 2

    def _place(solid, across_pos):
        if along_axis == "x":
            return solid.translate([at_along, across_pos, z])
        return solid.translate([across_pos, at_along, z])

    dimple = sphere(radius=radius + FIT_SLACK_MM / 2, **precision_kwargs())
    bump = sphere(radius=radius, **precision_kwargs())
    bumps = _place(bump, flank) | _place(bump, across - flank)
    # The bump engages sideways in the groove, so trimming its crown at the box's
    # top face costs nothing — and leaving it proud would make the closed box
    # taller than its declared height. The dimple is left untrimmed: it is cut
    # from the body, and opening it slightly at the rim is harmless.
    envelope = block([spec["width"], spec["length"], spec["height"]])
    return Closure(
        body=_place(dimple, flank) | _place(dimple, across - flank),
        lid=bumps & envelope,
    )


# ------------------------------------------------------------ filament hinge


def corner_catch(
    at: tuple[float, float],
    towards: tuple[float, float],
    radius: float,
    height: float,
    wall_thickness: float,
    rounding_edge: float | None = None,
    top_rounding: float | None = None,
    bottom_rounding: float | None = None,
) -> "Bosl2Solid":
    """A finger notch wrapping a corner, as the original's ``CornerCatch``.

    Not a new shape: the original builds it as **two `FingerHoleWall` scoops
    meeting at the corner**, one through each of the two walls, and this does
    the same with the same scoop builder. So the notch arrives with the roll,
    the floor fillet and the face fillets already right, and it cannot drift
    from the finger cuts elsewhere in the box.

    Args:
        at: The corner, in the piece's own frame.
        towards: Unit direction into the piece from that corner — ``(1, 1)``
            for the origin corner, ``(-1, -1)`` for the far one.
        radius: Half-width of each scoop.
        height: How far down from the top of the piece the notch reaches.
        wall_thickness: The wall each scoop cuts through.
        rounding_edge: Fillet where the cut meets each face; ``None`` uses the
            scoop default.
        top_rounding: ``r1`` — how far the mouth rolls in at the top. ``None``
            lets the scoop derive it from the half-width, which is what a
            sleeve notch wants; a cap box sets it, because there the pair of
            rolls is a fixed height budget rather than a proportion.
        bottom_rounding: ``r2`` — the roll out at the bottom of the cut.

    Returns:
        The solid to subtract from the piece.
    """
    from pyboxbuilder.compartments.finger_hole import build_wall_scoop
    from pyboxbuilder.compartments.element import union_all
    from pyboxbuilder.enums import ScoopSide

    # A span wide enough that the scoop is never capped by it; the scoop is
    # then slid from that span's midpoint onto the corner.
    span = max(4 * radius, 4 * wall_thickness)
    parts = []
    for side in (ScoopSide.FRONT, ScoopSide.LEFT):
        scoop = build_wall_scoop(
            span, span, height, side,
            radius=radius,
            wall_thickness=wall_thickness,
            rounding_edge=rounding_edge,
            rounding_radius=top_rounding,
            bottom_rounding=bottom_rounding,
            breach_floor=True,
            # There is material above a corner notch — the lid plate — so the
            # outline's rim overshoot is trimmed off rather than carving
            # through it.
            top_limit=height,
        )
        if side is ScoopSide.FRONT:
            scoop = scoop.translate([-span / 2, 0.0, 0.0])
        else:
            scoop = scoop.translate([0.0, -span / 2, 0.0])
        if towards[0] < 0:
            scoop = scoop.mirror([1, 0, 0])
        if towards[1] < 0:
            scoop = scoop.mirror([0, 1, 0])
        parts.append(scoop.translate([at[0], at[1], 0.0]))

    return union_all(parts)


def hinge_intrusion(spec: dict, filament_diameter: float = 1.75) -> "Bosl2Solid":
    """The volume a hinge occupies inside the box, as a solid to subtract.

    A hinge that sits inside the box's outline has to take that room from
    somewhere, and it takes it from the interior: the barrel and the leaf webs
    stand in the back of the box, right where a compartment would otherwise
    go. Rather than leave a compartment to collide with them, a hinge box
    subtracts this from its contents mask (following the original's
    `FilamentBoxInsideMask`, which does the same for the filament hinge).

    Args:
        spec: Box dimensions; reads `wall_thickness` and `lid_thickness`.
        filament_diameter: The pin stock, which sets the barrel radius.

    Returns:
        The solid the contents must keep clear of.
    """
    from pyboxbuilder.box.shell import block

    wt = spec.get("wall_thickness", 2.0)
    radius = max(wt, filament_diameter)
    reach = radius + 0.5 + PRINT_IN_PLACE_GAP_MM

    # A full-height slab is deliberate rather than a tight fit to the barrel:
    # a compartment that stops short of the hinge is what is wanted, and a
    # cavity that noses under a barrel it cannot quite reach is a place for a
    # piece to fall into and stay.
    return block(
        [spec["width"], reach, spec["height"] + 1.0],
        at=(0.0, spec["length"] - reach, -0.5),
    )


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

    # The pin runs along X, level with the joint between body and lid and set
    # **inside** the back wall: the barrel's outer face is flush with the box,
    # so the closed box is exactly its declared size with nothing hanging off
    # the back. The price is that the barrel intrudes into the interior, which
    # is why a hinge box carves that volume out of its contents mask.
    axis_y = spec["length"] - radius
    # Sunk far enough that the barrel's crown is flush with the *closed* box's
    # top, not just inside its footprint. `spec["height"]` here is the body's
    # height — the joint plane — and the lid adds its own thickness above it,
    # so a barrel wider than that thickness has to drop by the difference.
    axis_z = min(spec["height"], spec["height"] + leaf_thickness - radius)

    span = spec["width"] - 2 * wt
    pitch = span / knuckles
    # Each leaf webs inward from the barrel to its own half.
    web_y = axis_y
    web_depth = radius + 0.5

    body_parts, lid_parts = [], []
    body_relief, lid_relief = [], []
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
            # of the closed lid. It reaches *inward* now that the barrel is
            # inside the box.
            web = block(
                [length, web_depth, leaf_thickness - gap / 2],
                at=(centre_x - length / 2, web_y - web_depth, axis_z + gap / 2),
            )
            lid_parts += [knuckle, web]
            # The same knuckle and web, grown by the print gap: this is what
            # the body has to give up so the lid's leaf is a separate part.
            relief = cylinder(
                height=length + 2 * gap, radius=radius + gap, **precision_kwargs()
            ).rotate([0, 90, 0]).translate([centre_x, axis_y, axis_z])
            relief_web = block(
                [length + 2 * gap, web_depth + gap, leaf_thickness + gap],
                at=(
                    centre_x - length / 2 - gap,
                    web_y - web_depth - gap,
                    axis_z,
                ),
            )
            body_relief += [relief, relief_web]
        else:
            web = block(
                [length, web_depth, radius],
                at=(centre_x - length / 2, web_y - web_depth, axis_z - radius - gap / 2),
            )
            body_parts += [knuckle, web]
            # And the mirror image: what the lid gives up for this knuckle.
            lid_relief.append(
                cylinder(
                    height=length + 2 * gap, radius=radius + gap, **precision_kwargs()
                ).rotate([0, 90, 0]).translate([centre_x, axis_y, axis_z])
            )

    pin = cylinder(height=spec["width"] + 2, radius=bore, **precision_kwargs()).rotate([0, 90, 0])
    pin = pin.translate([spec["width"] / 2, axis_y, axis_z])
    # Split the barrel at the joint line so the two leaves cannot touch.
    parting = block(
        [spec["width"] + 2, web_depth + 2 * radius + 2, gap],
        at=(-1.0, web_y - web_depth - 1.0, axis_z - gap / 2),
    )

    body = union_all(body_parts)
    lid = union_all(lid_parts)
    return Closure(
        body=None if body is None else body - pin - parting,
        lid=None if lid is None else lid - pin - parting,
        body_cut=union_all(body_relief),
        lid_cut=union_all(lid_relief),
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
