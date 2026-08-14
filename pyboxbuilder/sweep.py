# SPDX-License-Identifier: Apache-2.0
"""Extruding a 2-D profile with rounded end rims.

The direct-CSG stand-in for BOSL2's
``offset_sweep(path, height=h, bottom=os_circle(rb), top=os_circle(rt))``, which
is how the original toolkit blends a cut smoothly into the face it emerges
from. Each rim arc is approximated by stacked slices of the profile's 2-D
offset, so everything stays Manifold-side CSG rather than an SDF or an
interpreted-BOSL2 region pipeline.

**Sign convention** (matching ``os_circle``):

- ``r > 0`` — convex **roundover**: the rim pulls *in* over that much height,
  so the end face is smaller than the body. Softens a protruding edge.
- ``r < 0`` — concave **flare** (a cove): the rim pushes *out*, tangent to the
  wall, so the end face is larger than the body. Used on a *cutting* solid,
  this is what fillets the cut into the surrounding face: the cut mouth opens
  out and meets the face tangentially instead of at a hard line.
- ``r == 0`` — a square end.

Because the finger scoops are subtractive, they want the **negative** radius:
that is the difference between a scoop that ends in a sharp shadow line on the
side of the box and one that flows onto it.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from pyboxbuilder.precision import kwargs as precision_kwargs

if TYPE_CHECKING:
    from pybosl2.shapes2d import Bosl2Shape2D
    from pybosl2.shapes3d import Bosl2Solid

DEFAULT_RIM_STEPS = 8
"""Slices per rim arc. At print scale the staircase on a 1–3mm rim is sub-pixel."""


def offset_sweep(
    profile: "Bosl2Shape2D",
    height: float,
    rounding_bottom: float = 0.0,
    rounding_top: float = 0.0,
    steps: int = DEFAULT_RIM_STEPS,
) -> "Bosl2Solid":
    """Extrude a 2-D profile from ``z=0`` to ``z=height``, rounding each rim.

    Args:
        profile: The 2-D shape to sweep.
        height: Total height of the sweep, **including** both end treatments.
        rounding_bottom: Bottom rim arc radius. Positive rounds over, negative
            flares out tangent to the wall, zero leaves it square.
        rounding_top: Top rim arc radius, same convention.
        steps: Number of offset slices approximating each rim arc. Raise it
            where a rim needs to be smoother than 8 slices.

    Returns:
        The swept solid, sitting on ``z=0``.

    Raises:
        ValueError: If ``height`` is not positive, or the two end treatments
            together do not fit inside ``height`` — a rim arc taller than the
            sweep would fold the solid through itself.
    """
    from pybosl2 import chain_hull

    from pyboxbuilder.precision import precision

    bottom, top = float(rounding_bottom), float(rounding_top)
    if height <= 0:
        raise ValueError(f"offset_sweep: height must be > 0; got {height}")
    if abs(bottom) + abs(top) > height + 1e-9:
        raise ValueError(
            f"offset_sweep: end treatments ({bottom}, {top}) do not fit in height {height}"
        )

    # A positive (convex) rim eats into the straight section; a negative
    # (concave) one grows outward from the end face and takes none of it.
    z0 = bottom if bottom > 0 else 0.0
    z1 = height - (top if top > 0 else 0.0)

    pieces = [profile.linear_extrude(height=float(z1 - z0), **precision_kwargs()).translate(
        [0.0, 0.0, float(z0)]
    )]

    resolution = steps if precision().fn is None else max(steps, precision().fn // 4)

    def rim(radius: float, at_bottom: bool) -> None:
        """Add one rim arc to ``pieces``, as a chain of hulled slices.

        Stacking prisms — one per slice, each at its own offset — is the obvious
        way to do this and it is what the legacy helper does, but it leaves a
        *staircase*: eight discrete steps across the fillet, each with a
        vertical wall, which is visible in a Manifold render at print scale and
        is not a fillet at all. Hulling consecutive slices instead fills the gap
        between them with a ruled surface, so the arc comes out monotone and
        smooth to the resolution of the slicing.
        """
        extent = abs(radius)
        if extent <= 1e-12:
            return

        def offset_at(distance: float) -> float:
            """The profile offset at ``distance`` along the arc from the end face."""
            if radius > 0:
                # Convex: fully inset at the end face, tangent to the wall at depth r.
                return -(radius - math.sqrt(max(0.0, radius * radius - (radius - distance) ** 2)))
            # Concave: fully outset at the end face, tangent to the wall at depth |r|.
            return math.sqrt(max(0.0, extent * extent - distance * distance))

        leaf = 1e-3  # A slice needs some thickness to be a solid at all.
        slices = []
        for index in range(resolution + 1):
            distance = extent * index / resolution
            delta = offset_at(distance)
            shape = (
                profile.offset(radius=delta, **precision_kwargs())
                if abs(delta) > 1e-12
                else profile
            )
            z = distance if at_bottom else height - distance - leaf
            slices.append(
                shape.linear_extrude(height=leaf, **precision_kwargs()).translate(
                    [0.0, 0.0, float(z)]
                )
            )

        pieces.append(chain_hull(slices))

    rim(bottom, at_bottom=True)
    rim(top, at_bottom=False)

    result = pieces[0]
    for piece in pieces[1:]:
        result = result | piece
    return result
