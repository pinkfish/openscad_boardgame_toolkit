# SPDX-License-Identifier: Apache-2.0
"""Rounding a box's exposed edges (FR-043, FR-044).

Nothing a hand grips should be a sharp 90° edge, which means the outer vertical
corners, the bottom edges and the top rim of every printed piece.

Rounding here is done by **subtracting the corner slivers** rather than by
intersecting with a rounded envelope. Both give the same rounded edges on an
ordinary box, but the intersection also silently trims anything reaching outside
the declared envelope — and a hinge barrel legitimately does (Phase 18 allows it
as the one bounded exception). Subtracting only the material a rounding would
remove leaves such features alone.

The radius defaults to ``wall_thickness / 2``: the largest fillet a wall can
carry while leaving half its thickness as flat face, and small enough to stay
clear of the lid features cut into the same walls.
"""

from __future__ import annotations

from typing import Sequence, TYPE_CHECKING

from pyboxbuilder.precision import kwargs as precision_kwargs

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


def default_rounding(wall_thickness: float) -> float:
    """The default edge radius for a wall of the given thickness.

    Args:
        wall_thickness: The box's wall thickness in mm.

    Returns:
        ``wall_thickness / 2`` — a 1mm fillet on a typical 2mm wall, which
        FR-044 names as an acceptable default.
    """
    return wall_thickness / 2


MATING_ROUNDING_RATIO = 0.5
"""How much of the outer radius a mating surface gets.

A partial lid — a cap's skirt, a slipover's sleeve — grips a band of the body,
so that band's corners and the lid's inner corners are a *fit*, not a finish.
They still want rounding (a square internal corner in a skirt is a stress riser
and a print artifact trap), but a smaller one: the skirt wall is only half a
wall thick, and a full-size fillet there would eat most of it.
"""


def mating_rounding(spec: dict) -> float:
    """The radius for surfaces where a partial lid grips the body.

    Both halves of the grip use this same value, so the lid's inner corners
    nest over the body's band corners instead of meeting them at a gap.

    Args:
        spec: Reads `inner_rounding` for an explicit value, else derives it
            from the body radius.

    Returns:
        The radius in mm; ``0`` leaves the mating corners square.
    """
    from pyboxbuilder.box.shell import body_rounding

    explicit = spec.get("inner_rounding")
    if explicit is not None:
        return max(0.0, float(explicit))
    return body_rounding(spec) * MATING_ROUNDING_RATIO


def rounded_block(
    size: Sequence[float],
    rounding: float,
    edges: Sequence,
    at: Sequence[float] = (0.0, 0.0, 0.0),
) -> "Bosl2Solid":
    """A corner-placed block with some of its edges rounded.

    Args:
        size: The block's ``(width, length, height)``.
        rounding: Edge radius in mm. Zero, or too large for the block, gives a
            plain square block rather than an error — callers are passing a
            project-wide default down to pieces of every size.
        edges: pybosl2 ``edges=`` selector naming which edges to round.
        at: Where the block's minimum corner sits.

    Returns:
        The block, rounded where asked.
    """
    from pybosl2 import cuboid

    from pyboxbuilder.box.shell import block, corner

    if rounding <= 0 or rounding > max_radius(size, edges):
        return block(list(size), at)
    return corner(
        cuboid(list(size), rounding=rounding, edges=list(edges), **rounding_facets()),
        size,
        at,
    )


def vertical_edges() -> list:
    """Edge selector for a box's four vertical corners.

    ``Anchor.Z`` looks like the obvious way to say this and is **wrong**: it is
    an *axis* anchor, and the edge language resolves it to a single edge, so a
    box asked to round its vertical corners came back with exactly one of them
    rounded. The four two-face anchors resolve to the full ``[1, 1, 1, 1]``
    vertical row.

    Returns:
        The pybosl2 ``edges=`` selector naming all four vertical edges.
    """
    from pybosl2 import Anchor

    return [Anchor.FRONT_LEFT, Anchor.FRONT_RIGHT, Anchor.BACK_LEFT, Anchor.BACK_RIGHT]


def vertical_and_bottom_edges() -> list:
    """Edge selector for a body: the four vertical corners and the base.

    Returns:
        The pybosl2 ``edges=`` selector for the edges a hand grips on a box
        body, leaving the top rim alone because that is where a lid mates.
    """
    from pybosl2 import Anchor

    return vertical_edges() + [Anchor.BOTTOM]


def vertical_and_top_edges() -> list:
    """Edge selector for a lid, or for the free rim of a lidless box.

    Returns:
        The pybosl2 ``edges=`` selector for the four vertical corners and the
        top face's edges — the exposed edges of a closed box's upper surface.
    """
    from pybosl2 import Anchor

    return vertical_edges() + [Anchor.TOP]


def max_radius(size: Sequence[float], edges: Sequence) -> float:
    """The largest radius these edges can carry on a block of ``size``.

    A blanket ``min(size) / 2`` is the tempting guard and it is wrong often
    enough to matter: it rejects an 8mm fillet on the floor of a 12mm-deep
    tray, which is perfectly buildable, because the *depth* is the smallest
    dimension. What actually constrains a fillet is the dimensions
    perpendicular to the edge it runs along, and then only halved where the
    edge on the **opposite** side is being rounded too — two fillets growing
    towards each other meet at half the gap, but one growing alone can use all
    of it.

    Args:
        size: The block's ``(width, length, height)``.
        edges: pybosl2 ``edges=`` selector.

    Returns:
        The maximum radius in mm, or ``inf`` when no edge is selected.
    """
    from pybosl2._edges_lang import EDGE_OFFSETS, edges as resolve

    matrix = resolve(list(edges) if isinstance(edges, (list, tuple)) else edges)
    limits: list[float] = []
    for axis, row in enumerate(matrix):
        active = [EDGE_OFFSETS[axis][i] for i, on in enumerate(row) if on]
        if not active:
            continue
        for other in range(3):
            if other == axis:
                continue  # the edge runs along this one; it is not a constraint
            signs = {offset[other] for offset in active}
            limits.append(size[other] / 2 if len(signs) > 1 else size[other])
    return min(limits) if limits else float("inf")


def edge_slivers(
    size: Sequence[float],
    rounding: float,
    edges: Sequence,
    at: Sequence[float] = (0.0, 0.0, 0.0),
) -> "Bosl2Solid":
    """The material a rounding removes: the square block minus the rounded one.

    Args:
        size: The block's ``(width, length, height)``.
        rounding: Edge radius in mm; must be positive.
        edges: pybosl2 ``edges=`` selector naming which edges to round.
        at: Where the block's minimum corner sits.

    Returns:
        A solid occupying only the corner slivers, ready to subtract.

    Raises:
        ValueError: If ``rounding`` is not positive, or is at least half the
            smallest dimension — a fillet that large has no flat face left to
            blend into and folds the solid through itself.
    """
    from pybosl2 import cuboid

    from pyboxbuilder.box.shell import block, corner

    if rounding <= 0:
        raise ValueError(f"rounding must be > 0; got {rounding}")
    limit = max_radius(size, edges)
    if rounding > limit:
        raise ValueError(
            f"rounding {rounding} is too large for size {tuple(size)} on these "
            f"edges; the limit is {limit}"
        )

    square = block(list(size), at)
    rounded = corner(
        cuboid(list(size), rounding=rounding, edges=list(edges), **rounding_facets()),
        size,
        at,
    )
    return square - rounded


MIN_ROUNDING_FACETS = 48
"""Facets per full circle for an edge fillet, however small its radius.

Two reasons this floor exists, and the second sets the number:

1. The default ``fs = 2mm`` sizes a facet by arc *length*, which is right for a
   cylinder and wrong for a fillet: a 1mm roundover has a 1.6mm quarter-arc, so
   it gets a single segment and prints — and renders — as a **chamfer**.
2. A rounded edge is an *inscribed* polygon, so the face it blends into is
   pulled in by the sagitta, ``r · (1 - cos(180°/fn))``. That shrinks the box
   below its declared size, which the packer and the spacers both rely on. At
   16 facets a 1.5mm fillet costs 0.029mm — small, but above the 0.01mm noise
   floor; at 48 it is 0.003mm, comfortably under it and under the 0.1mm
   dimensional precision the library promises.
"""


def rounding_facets() -> dict:
    """Tessellation arguments for an edge fillet.

    Returns:
        The precision in force, with a floor on the facet count so a small
        radius still comes out curved rather than chamfered. An explicit,
        higher ``fn`` from the caller wins.
    """
    from pyboxbuilder.precision import precision

    settings = precision()
    values = dict(settings.kwargs())
    values["fn"] = max(settings.fn or 0, MIN_ROUNDING_FACETS)
    return values


def round_edges(
    solid: "Bosl2Solid",
    size: Sequence[float],
    rounding: float,
    edges: Sequence,
    at: Sequence[float] = (0.0, 0.0, 0.0),
) -> "Bosl2Solid":
    """Round ``solid``'s edges over the envelope ``size`` at ``at``.

    Args:
        solid: The solid to round.
        size: The envelope the rounding is measured against — normally the
            box's declared ``(width, length, height)``.
        rounding: Edge radius in mm. Zero or negative leaves ``solid`` alone.
        edges: pybosl2 ``edges=`` selector naming which edges to round.
        at: Where the envelope's minimum corner sits.

    Returns:
        The solid with those edges rounded. Material outside the envelope —
        a hinge barrel, say — is untouched.
    """
    if rounding <= 0 or rounding > max_radius(size, edges):
        # Too large to be buildable on this piece; leave it square rather than
        # raising, since the caller is applying a project-wide default.
        return solid
    return solid - edge_slivers(size, rounding, edges, at)
