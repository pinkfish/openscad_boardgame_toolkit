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

    Args:
        spec: Reads `lid_thickness`; an explicit `lead_chamfer` wins.

    Returns:
        The chamfer depth in mm — half the lid thickness by default.
    """
    lt = spec.get("lid_thickness", 2.0)
    return spec.get("lead_chamfer", lt / 2)


def _dovetail_frustum(
    along_axis: str,
    bottom_center: tuple[float, float],
    bottom_size: tuple[float, float],
    top_center: tuple[float, float],
    top_size: tuple[float, float],
    height: float,
    z0: float,
) -> "Bosl2Solid":
    """A frustum dovetailed on both sides and the back, straight at the front.

    The bottom and top faces are rectangles described by their ``(along,
    across)`` centre and size in the slide frame. The top centre is offset
    toward the open end relative to the bottom centre, which is what keeps the
    front face vertical while the back and both flanks taper.
    """
    from pybosl2.shapes3d import prismoid

    shift_along = top_center[0] - bottom_center[0]
    shift_across = top_center[1] - bottom_center[1]

    if along_axis == "x":
        solid = prismoid(
            [bottom_size[0], bottom_size[1]],
            [top_size[0], top_size[1]],
            height=height,
            shift=[shift_along, shift_across],
            **precision_kwargs(),
        )
        return solid.translate([bottom_center[0], bottom_center[1], z0])
    solid = prismoid(
        [bottom_size[1], bottom_size[0]],
        [top_size[1], top_size[0]],
        height=height,
        shift=[shift_across, shift_along],
        **precision_kwargs(),
    )
    return solid.translate([bottom_center[1], bottom_center[0], z0])


def _lead_chamfer(
    along_axis: str,
    lead: float,
    across_min: float,
    across_max: float,
    z_bottom: float,
    size: float,
) -> "Bosl2Solid":
    """A 45° wedge beveling the lid's leading bottom edge.

    ``lead`` is the leading end's coordinate along the slide axis — the face
    that enters the box first. The wedge is full height ``size`` at that face
    and tapers to nothing ``size`` further in, across the lid's full width, so
    the lid starts into the grooves instead of catching on their mouths.
    """
    from pybosl2.shapes3d import prismoid

    span = across_max - across_min
    across_center = (across_min + across_max) / 2
    if along_axis == "x":
        solid = prismoid(
            [size, span], [0.0, span], height=size, shift=[-size / 2, 0.0],
            **precision_kwargs(),
        )
        return solid.translate([lead + size / 2, across_center, z_bottom])
    solid = prismoid(
        [span, size], [span, 0.0], height=size, shift=[0.0, -size / 2],
        **precision_kwargs(),
    )
    return solid.translate([across_center, lead + size / 2, z_bottom])


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

    The back of the channel is dovetailed exactly like the two sides: the stop
    wall keeps its full thickness at the top and half of it at the bottom, so
    the lid's leading end seats in a matching back groove instead of butting
    against a flat wall.

    The lid is the matching frustum — dovetailed on both sides and the back,
    straight at the front — cut short by `sliding_slack` on every mating face
    so it slides freely, with a slight chamfer on its leading end (FR-002c,
    FR-002d). The lid fills the channel flush with the open end.

    Args:
        spec: Needs `width`, `length`, `height`; reads `wall_thickness`,
            `lid_thickness`, and optionally `lead_chamfer` and `sliding_slack`
            (per-side clearance, default 0.1mm).
        along_axis: ``"x"`` to slide along the width, ``"y"`` along the length.

    Returns:
        The channel to subtract from the body, and the lid that fills it.
    """
    wt = spec.get("wall_thickness", 2.0)
    lt = spec.get("lid_thickness", 2.0)
    s = spec.get("sliding_slack", 0.1)
    chamfer = lead_chamfer_size(spec)
    top_key, bottom_key = sliding_dovetail(spec)

    if along_axis == "x":
        along = spec["width"]
        across = spec["length"]
    else:
        along = spec["length"]
        across = spec["width"]

    z0 = spec["height"] - lt
    interior_along = along - 2 * wt
    interior_across = across - 2 * wt

    # The lid: a frustum dovetailed on both sides and the back, straight at the
    # front. Its top face is the interior (no key) and its underside reaches
    # `bottom_key` into each wall, cut short by the clearance on every face.
    lid = _dovetail_frustum(
        along_axis,
        ((along + wt - bottom_key) / 2, across / 2),
        (interior_along + wt + bottom_key - 2 * s,
         interior_across + 2 * bottom_key - 2 * s),
        ((along + wt - top_key) / 2, across / 2),
        (interior_along + wt + top_key - 2 * s,
         interior_across + 2 * top_key - 2 * s),
        lt,
        z0,
    )

    # The channel: the same frustum, larger by the clearance and a hair. Its
    # floor reaches `bottom_key` into each wall, its opening `top_key`, and its
    # front runs out through the open end wall.
    channel = _dovetail_frustum(
        along_axis,
        ((along + wt - bottom_key) / 2, across / 2),
        (interior_along + wt + bottom_key + 0.1,
         interior_across + 2 * bottom_key + 0.1),
        ((along + wt - top_key) / 2, across / 2),
        (interior_along + wt + top_key + 0.1,
         interior_across + 2 * top_key + 0.1),
        lt + 0.1,
        z0 - 0.05,
    )

    # A slight chamfer on the leading (back) end's bottom edge eases the lid
    # into the grooves.
    if chamfer > 0:
        lead = wt - bottom_key + s
        lid = lid - _lead_chamfer(
            along_axis, lead, lead, across - wt + bottom_key - s, z0, chamfer
        )

    return Closure(body=channel, lid=lid)


def sliding_track(spec: dict) -> Closure:
    """The sliding channel and lid, in the slide-along-X frame.

    A thin wrapper over :func:`dovetail_track` for the types that always slide
    along X (``SlidingCatchBox``, ``CardLibraryBox``).
    """
    return dovetail_track(spec, "x")


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


def corner_catch(
    at: tuple[float, float],
    towards: tuple[float, float],
    radius: float,
    height: float,
    wall_thickness: float,
    rounding_edge: float | None = None,
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
