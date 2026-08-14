# SPDX-License-Identifier: Apache-2.0
"""Guillotine box packer for densely-filled inserts (T187).

The extreme-point First-Fit-Decreasing solver in `layout.py` places boxes at
corner points, which fragments the free space: above roughly 70% fill it cannot
find arrangements that demonstrably exist. Emberleaf is the standing example --
18 boxes at 77% fill, whose sizes tile exactly in three columns, and which
266,000 random permutations of that solver never packed.

This solver searches a different space. Instead of tracking corner points it
tracks free *regions*, and placing a box cuts the region it went into. Three
things make that work where the corner-point search did not:

**Support is structural, not checked.** A box may only be opened above another
box's own top face, or above a layer that is required to be filled solid (see
`Region.full`). The corner-point search floats a box with one corner resting on
another; bolting an explicit support test onto it made the search 3000x more
expensive and it still failed.

**Feasibility depends on region sizes alone.** The regions are disjoint, so
where they are cannot affect whether the remaining boxes fit -- only how big
they are. That makes the memo key position-free, which is what keeps the state
count small enough to search exhaustively.

**Smallest region first.** The fail-first principle, and the single biggest
lever here: the most constrained region has the fewest options, so a dead end
surfaces immediately instead of after the rest of the box is filled around it.
Measured on Emberleaf, taking the largest region first fails to find any packing
in 1,000,000 nodes; taking the smallest finds one in 3,237.
"""

from __future__ import annotations

from dataclasses import dataclass

EPS = 1e-9
"""Comparison tolerance in mm. Well under any printable dimension."""

PLACES = 6
"""Decimal places region sizes are rounded to.

Repeated subtraction leaves dust like 71.24999999999999, which would stop two
states that are really the same from sharing a memo entry.
"""


@dataclass(frozen=True)
class Item:
    """A box to place."""

    label: str
    size: tuple[float, float, float]
    no_rotate: bool = False


@dataclass(frozen=True)
class Placed:
    """Where one box ended up."""

    label: str
    position: tuple[float, float, float]
    size: tuple[float, float, float]
    rotated: bool


def _orientations(size: tuple[float, float, float], no_rotate: bool):
    """The ways a box may be turned.

    Only the quarter turn about Z: a box printed with its lid on top has to stay
    that way up.
    """
    w, l, h = size
    yield (w, l, h), False
    if not no_rotate and abs(w - l) > EPS:
        yield (l, w, h), True


# A region is (x, y, z, w, l, h, full). `full` marks a region that MUST be
# filled to its own full height, because something rests on top of it. Only a
# box exactly as tall as the region may go in one, and its leftovers inherit the
# obligation. Without that flag a layer cut would let a box bridge over a
# half-filled layer with nothing underneath it.


def pack_guillotine(
    container: tuple[float, float, float],
    items: list[Item],
    *,
    node_budget: int = 200_000,
) -> list[Placed] | None:
    """Pack `items` into `container`, or return None if this search cannot.

    Returns None rather than raising: the caller decides whether to fall back to
    another solver or to report the failure. None is not proof that no packing
    exists -- `node_budget` may simply have run out.

    Args:
        container: (width, length, height) of the space to fill.
        items: The boxes. Identical ones are searched as a single class, so five
            copies of one box cost no more than one.
        node_budget: Search nodes before giving up. The 18-box Emberleaf layout
            resolves in 3,237 of them, in about 30ms; the budget is headroom for
            harder inputs, not a figure normal ones approach.
    """
    if not items:
        return []

    # Identical boxes are interchangeable, so search them as one class and hand
    # the labels back out at the end. This is what stops five identical player
    # boxes from multiplying the search by 5!.
    classes: list[tuple[tuple[float, float, float], bool]] = []
    labels: list[list[str]] = []
    for item in items:
        w, l, h = item.size
        key = ((float(w), float(l), float(h)), item.no_rotate)
        if key in classes:
            labels[classes.index(key)].append(item.label)
        else:
            classes.append(key)
            labels.append([item.label])

    counts = tuple(len(group) for group in labels)
    smallest_dim = min(min(size) for size, _ in classes)
    total_volume = sum(
        n * size[0] * size[1] * size[2] for n, (size, _) in zip(counts, classes)
    )

    nodes = 0
    dead: set = set()

    def usable(region):
        """Whether a region is big enough to be worth keeping in the pool."""
        return min(region[3], region[4], region[5]) >= smallest_dim - EPS

    def splits(region, size):
        """Every way of cutting `region` once a box sits in its origin corner.

        Yields tuples of sub-regions, or None for a split that is not allowed.

        Two families:

        * **Corner** -- the box's own faces cut the region, and the only space
          opened above the box is the column standing on it. Two variants,
          differing in which side slab runs the full depth.
        * **Layer** -- cut clean across the region at the box's height first, so
          the space above spans the whole footprint rather than one box's top.
          This is what lets a box bridge two boxes below it, which is how real
          inserts stack, and the corner family cannot express it. The rest of the
          layer is marked `full` so it has to be filled solid; otherwise the
          bridge would span a void.
        """
        x, y, z, w, l, h, full = region
        bw, bl, bh = size
        gap_h = round(h - bh, PLACES)

        for x_major in (True, False):
            if x_major:
                sides = (
                    (x + bw, y, z, round(w - bw, PLACES), l, h, full),
                    (x, y + bl, z, bw, round(l - bl, PLACES), h, full),
                )
            else:
                sides = (
                    (x, y + bl, z, w, round(l - bl, PLACES), h, full),
                    (x + bw, y, z, round(w - bw, PLACES), bl, h, full),
                )

            # Corner: space above the box is exactly the box's top face.
            if not full or gap_h <= EPS:
                above = (x, y, z + bh, bw, bl, gap_h, False)
                yield tuple(
                    r for r in sides + (above,)
                    if min(r[3], r[4], r[5]) > EPS and usable(r)
                )

            # Layer: cut across at the box's height. The rest of this layer must
            # be filled solid, so anything placed above it is fully supported.
            if gap_h > EPS and not full:
                layer_sides = tuple(
                    (sx, sy, sz, sw, sl, bh, True)
                    for (sx, sy, sz, sw, sl, _sh, _f) in sides
                    if min(sw, sl) > EPS
                )
                # An unfillable sliver in the layer makes the whole cut invalid:
                # it would leave a void with a box bridging over it.
                if any(not usable(r) for r in layer_sides):
                    continue
                yield layer_sides + ((x, y, z + bh, w, l, gap_h, False),)

    def solve(regions, remaining, need):
        nonlocal nodes
        nodes += 1
        if nodes > node_budget:
            return None
        if not any(remaining):
            # Any region still demanding to be filled solid means a box above it
            # would bridge a void.
            return [] if not any(r[6] for r in regions) else None
        if not regions:
            return None
        if sum(r[3] * r[4] * r[5] for r in regions) < need - EPS:
            return None

        key = (tuple(sorted(r[3:] for r in regions)), remaining)
        if key in dead:
            return None

        # Smallest region first -- see the module docstring. A region that must
        # be filled solid comes first of all: it has the least freedom.
        index = min(
            range(len(regions)),
            key=lambda i: (not regions[i][6],
                           regions[i][3] * regions[i][4] * regions[i][5]),
        )
        region = regions[index]
        rest = regions[:index] + regions[index + 1:]
        rw, rl, rh, must_fill = region[3], region[4], region[5], region[6]

        candidates = []
        for i, (size, no_rotate) in enumerate(classes):
            if not remaining[i]:
                continue
            for turned, rotated in _orientations(size, no_rotate):
                w, l, h = turned
                if w > rw + EPS or l > rl + EPS or h > rh + EPS:
                    continue
                if must_fill and abs(h - rh) > EPS:
                    continue  # a short box here would leave a void above it
                # Prefer a box that finishes flush with the region's walls: a
                # flush face leaves no sliver behind it.
                flush = (
                    (abs(w - rw) < EPS) + (abs(l - rl) < EPS) + (abs(h - rh) < EPS)
                )
                # `rotated` ahead of the class index keeps a box the way up the
                # caller declared it unless turning actually buys something. A
                # box that fits either way should come out unturned, or the
                # printed part changes orientation for no reason.
                candidates.append(
                    (-flush, -(w * l * h), int(rotated), i, turned, rotated)
                )
        candidates.sort()

        for _flush, _volume, _turn, i, turned, rotated in candidates:
            shapes_tried = set()
            for subs in splits(region, turned):
                shape = tuple(sorted(s[3:] for s in subs))
                if shape in shapes_tried:
                    continue  # another variant already cut it this way
                shapes_tried.add(shape)

                nxt = list(remaining)
                nxt[i] -= 1
                tail = solve(
                    tuple(sorted(rest + subs)),
                    tuple(nxt),
                    need - turned[0] * turned[1] * turned[2],
                )
                if tail is not None:
                    return [
                        (region[0], region[1], region[2], turned, rotated, i)
                    ] + tail

        # Nothing fits, or nothing that fits leads anywhere. A plain region can
        # be given up as waste; one that owes a solid fill cannot.
        if not must_fill:
            tail = solve(rest, remaining, need)
            if tail is not None:
                return tail

        dead.add(key)
        return None

    root = (
        0.0, 0.0, 0.0,
        round(float(container[0]), PLACES),
        round(float(container[1]), PLACES),
        round(float(container[2]), PLACES),
        False,
    )
    solution = solve((root,), counts, total_volume)
    if solution is None:
        return None

    pool = [list(group) for group in labels]
    return [
        Placed(
            label=pool[i].pop(0),
            position=(x, y, z),
            size=size,
            rotated=rotated,
        )
        for (x, y, z, size, rotated, i) in solution
    ]
