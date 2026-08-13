# SPDX-License-Identifier: Apache-2.0
"""Spacer tray generation — fill the leftover space with as few trays as possible.

Three stages (FR-014, FR-014a/b/c):

1. **Sweep** the game box for the volume no sub-box occupies, and decompose that
   volume into axis-aligned boxes, largest first.
2. **Merge** any two boxes whose union is itself a box, to a fixed point.
3. **Shrink** each survivor by the clearance slack and drop the ones too thin to
   print.

Stage 1 takes the largest box available at each step rather than scanning the
grid in index order, and stage 2 exists at all, for the same reason: the plane
grid is global, so a box in one corner of the game box contributes cut planes
that slice free space everywhere else. Index-order scanning lets a 2 mm sliver
claim cells out of the middle of a large void and leave it in fragments — the
number of trays then depends on how many boxes the layout happens to contain,
which is what FR-014a forbids.
"""

from __future__ import annotations

from dataclasses import dataclass

EPSILON = 0.01
"""Coordinates closer than this are the same plane."""

MIN_SPACER_DIM = 5.0
"""A tray thinner than this in any axis is too fragile to print (FR-014)."""

MAX_GRID_CELLS = 200_000
"""Above this the largest-first search is skipped for the cheap index-order scan."""


@dataclass(frozen=True)
class SpacerSpec:
    """Configuration for a single spacer tray."""

    label: str
    width: float
    length: float
    height: float
    position: tuple[float, float, float]


@dataclass(frozen=True)
class Void:
    """An empty region: a box, or a prism over a non-rectangular footprint.

    `position` and `size` are always the axis-aligned bounding box. `path`, when
    set, is the real footprint outline in absolute X/Y — an L, T or U left over
    between boxes (FR-018).
    """

    position: tuple[float, float, float]
    size: tuple[float, float, float]
    path: tuple[tuple[float, float], ...] | None = None

    @property
    def volume(self) -> float:
        if self.path is not None:
            return _polygon_area(self.path) * self.size[2]
        return self.size[0] * self.size[1] * self.size[2]

    def far_corner(self) -> tuple[float, float, float]:
        return tuple(p + s for p, s in zip(self.position, self.size))  # type: ignore[return-value]

    def thinnest(self) -> float:
        return min(self.size)

    def relative_path(self) -> tuple[tuple[float, float], ...] | None:
        """`path` moved into the void's own frame, which is what PathBox wants."""
        if self.path is None:
            return None
        return tuple(
            (x - self.position[0], y - self.position[1]) for x, y in self.path
        )


# --------------------------------------------------------------------- sweep


def _plane_grid(container, placements) -> tuple[list[float], list[float], list[float]]:
    """The sorted X/Y/Z planes bounding every box and the container itself."""
    axes: list[set[float]] = [{0.0, float(container[i])} for i in range(3)]
    for placement in placements:
        for i in range(3):
            axes[i].add(float(placement.position[i]))
            axes[i].add(float(placement.position[i] + placement.size[i]))
    return tuple(  # type: ignore[return-value]
        [v for v in sorted(axis) if -EPSILON <= v <= container[i] + EPSILON]
        for i, axis in enumerate(axes)
    )


def _occupancy(planes, placements) -> list[list[list[bool]]]:
    """Mark every grid cell that lies inside a placed box."""
    xs, ys, zs = planes
    nx, ny, nz = len(xs) - 1, len(ys) - 1, len(zs) - 1
    occupied = [[[False] * nz for _ in range(ny)] for _ in range(nx)]

    for placement in placements:
        px, py, pz = placement.position
        pw, pl, ph = placement.size
        for i in range(nx):
            if not (xs[i] >= px - EPSILON and xs[i + 1] <= px + pw + EPSILON):
                continue
            for j in range(ny):
                if not (ys[j] >= py - EPSILON and ys[j + 1] <= py + pl + EPSILON):
                    continue
                for k in range(nz):
                    if zs[k] >= pz - EPSILON and zs[k + 1] <= pz + ph + EPSILON:
                        occupied[i][j][k] = True
    return occupied


def _grow(taken, start, counts) -> tuple[int, int, int]:
    """Grow the largest cell box from `start`: +x as far as it goes, then +y, then +z."""
    i, j, k = start
    nx, ny, nz = counts

    i2 = i
    while i2 < nx and not taken[i2][j][k]:
        i2 += 1

    j2 = j + 1
    while j2 < ny and all(not taken[ii][j2][k] for ii in range(i, i2)):
        j2 += 1

    k2 = k + 1
    while k2 < nz and all(
        not taken[ii][jj][k2] for ii in range(i, i2) for jj in range(j, j2)
    ):
        k2 += 1

    return i2, j2, k2


def sweep_free_space(container, placements) -> list[Void]:
    """Decompose the space no placement occupies into boxes, largest first.

    Taking the biggest box available at each step is what keeps a big void in one
    piece: a sliver alongside it would otherwise claim cells out of its middle
    and leave it split (FR-014a).

    Args:
        container: (width, length, height) of the volume to fill.
        placements: The boxes already placed in it.

    Returns:
        Disjoint `Void`s covering all of the free space, in descending volume.
    """
    if not placements:
        return []

    planes = _plane_grid(container, placements)
    xs, ys, zs = planes
    counts = (len(xs) - 1, len(ys) - 1, len(zs) - 1)
    if min(counts) <= 0:
        return []

    taken = _occupancy(planes, placements)
    largest_first = counts[0] * counts[1] * counts[2] <= MAX_GRID_CELLS

    def void_from(start, end) -> Void:
        i, j, k = start
        i2, j2, k2 = end
        return Void(
            position=(xs[i], ys[j], zs[k]),
            size=(xs[i2] - xs[i], ys[j2] - ys[j], zs[k2] - zs[k]),
        )

    voids: list[Void] = []
    while True:
        best: tuple[Void, tuple[int, int, int], tuple[int, int, int]] | None = None
        for i in range(counts[0]):
            for j in range(counts[1]):
                for k in range(counts[2]):
                    if taken[i][j][k]:
                        continue
                    end = _grow(taken, (i, j, k), counts)
                    candidate = void_from((i, j, k), end)
                    if best is None or candidate.volume > best[0].volume:
                        best = (candidate, (i, j, k), end)
                    if not largest_first:
                        break
                if best is not None and not largest_first:
                    break
            if best is not None and not largest_first:
                break

        if best is None:
            return voids

        void, (i, j, k), (i2, j2, k2) = best
        for ii in range(i, i2):
            for jj in range(j, j2):
                for kk in range(k, k2):
                    taken[ii][jj][kk] = True
        voids.append(void)


# --------------------------------------------------------------------- merge


def _mergeable_axis(a: Void, b: Void) -> int | None:
    """The axis along which `a` and `b` fuse into one box, or None.

    They fuse when they meet face to face on one axis and match exactly on the
    other two — the union then covers the two originals and nothing else, so it
    can never swallow occupied space.
    """
    for axis in range(3):
        others = [i for i in range(3) if i != axis]
        if any(
            abs(a.position[i] - b.position[i]) > EPSILON
            or abs(a.size[i] - b.size[i]) > EPSILON
            for i in others
        ):
            continue
        a_far, b_far = a.far_corner(), b.far_corner()
        if (
            abs(a_far[axis] - b.position[axis]) <= EPSILON
            or abs(b_far[axis] - a.position[axis]) <= EPSILON
        ):
            return axis
    return None


def _fuse(a: Void, b: Void, axis: int) -> Void:
    position = list(a.position)
    size = list(a.size)
    position[axis] = min(a.position[axis], b.position[axis])
    size[axis] = a.size[axis] + b.size[axis]
    return Void(position=tuple(position), size=tuple(size))  # type: ignore[arg-type]


def merge_voids(voids: list[Void]) -> list[Void]:
    """Fuse mergeable voids until none remain (FR-014b).

    Every fusion drops the count by one, so this terminates in at most N rounds.
    Voids are visited in a canonical order, which makes the result depend only on
    the geometry and not on the order the sweep happened to find them in — note
    that this is determinism, not uniqueness: an L-shaped run of three voids can
    legitimately fuse two different ways, and both leave two boxes behind.
    """
    remaining = sorted(voids, key=lambda v: (v.position, v.size))

    fused = True
    while fused:
        fused = False
        for index_a, a in enumerate(remaining):
            for offset, b in enumerate(remaining[index_a + 1:]):
                axis = _mergeable_axis(a, b)
                if axis is None:
                    continue
                index_b = index_a + 1 + offset
                merged = _fuse(a, b, axis)
                remaining = [
                    v for n, v in enumerate(remaining) if n not in (index_a, index_b)
                ]
                remaining.append(merged)
                remaining.sort(key=lambda v: (v.position, v.size))
                fused = True
                break
            if fused:
                break

    return remaining


# -------------------------------------------------- rectilinear merge (FR-018)


def _polygon_area(path) -> float:
    from pyboxbuilder.paths import polygon_area

    return polygon_area(path)


def _footprints_touch(a: Void, b: Void) -> bool:
    """True when two footprints share a border segment of non-zero length."""
    for axis in range(2):
        other = 1 - axis
        a_lo, a_hi = a.position[axis], a.position[axis] + a.size[axis]
        b_lo, b_hi = b.position[axis], b.position[axis] + b.size[axis]
        flush = abs(a_hi - b_lo) <= EPSILON or abs(b_hi - a_lo) <= EPSILON
        if not flush:
            continue
        overlap = min(
            a.position[other] + a.size[other], b.position[other] + b.size[other]
        ) - max(a.position[other], b.position[other])
        if overlap > EPSILON:
            return True
    return False


def _components(voids: list[Void]) -> list[list[Void]]:
    """Group voids into connected clusters by footprint adjacency."""
    unassigned = list(voids)
    groups: list[list[Void]] = []
    while unassigned:
        group = [unassigned.pop()]
        grew = True
        while grew:
            grew = False
            for candidate in list(unassigned):
                if any(_footprints_touch(candidate, member) for member in group):
                    group.append(candidate)
                    unassigned.remove(candidate)
                    grew = True
        groups.append(group)
    return groups


def union_outline(voids: list[Void]) -> tuple[tuple[float, float], ...]:
    """Trace the outline of a union of axis-aligned footprints.

    Works by cancellation: walk each cell's border counter-clockwise, and drop
    any edge that also appears reversed — those are the internal seams between
    two filled cells. What survives is the boundary, which then chains into a
    loop. Collinear runs are collapsed so an L comes back as six points, not
    every grid step along its sides.
    """
    xs = sorted({v.position[0] for v in voids} | {v.position[0] + v.size[0] for v in voids})
    ys = sorted({v.position[1] for v in voids} | {v.position[1] + v.size[1] for v in voids})

    filled: set[tuple[int, int]] = set()
    for void in voids:
        for i in range(len(xs) - 1):
            if not (
                xs[i] >= void.position[0] - EPSILON
                and xs[i + 1] <= void.position[0] + void.size[0] + EPSILON
            ):
                continue
            for j in range(len(ys) - 1):
                if (
                    ys[j] >= void.position[1] - EPSILON
                    and ys[j + 1] <= void.position[1] + void.size[1] + EPSILON
                ):
                    filled.add((i, j))

    edges: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    for i, j in sorted(filled):
        corners = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
        for n in range(4):
            start, end = corners[n], corners[(n + 1) % 4]
            if (end, start) in edges:
                edges.discard((end, start))  # internal seam — cancels with its twin
            else:
                edges.add((start, end))

    if not edges:
        return ()

    # A reflex corner is the start of two boundary edges, so this has to be a
    # multimap — keying by start vertex alone drops one of them and the trace
    # below then never closes.
    outgoing: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for start, end in sorted(edges):
        outgoing.setdefault(start, []).append(end)

    first = min(outgoing)
    loop = [first]
    node = outgoing[first].pop()
    while node != first:
        loop.append(node)
        options = outgoing.get(node)
        if not options:  # not a closed ring; caller keeps the pieces apart
            return ()
        node = options.pop()
        if len(loop) > len(edges) + 1:  # cannot happen, but never spin
            return ()

    return _drop_collinear([(xs[i], ys[j]) for i, j in loop])


def _drop_collinear(points) -> tuple[tuple[float, float], ...]:
    """Remove points that sit in the middle of a straight run."""
    kept = []
    for n, point in enumerate(points):
        before = points[n - 1]
        after = points[(n + 1) % len(points)]
        straight = (
            abs(before[0] - point[0]) <= EPSILON and abs(point[0] - after[0]) <= EPSILON
        ) or (
            abs(before[1] - point[1]) <= EPSILON and abs(point[1] - after[1]) <= EPSILON
        )
        if not straight:
            kept.append(point)
    return tuple(kept)


def merge_rectilinear(voids: list[Void]) -> list[Void]:
    """Fuse coplanar neighbours into one polygon-footprint tray (FR-018).

    After `merge_voids` has taken every rectangular fusion, what can be left is
    an L, T or U — a shape no rectangle covers. Those still want to be one part,
    so they become a single tray with a polygon footprint.

    Only voids sharing an **identical Z span** are considered. Two voids at
    different heights can also form an L, but in the vertical plane, and fusing
    those is a mistake: the upper arm would have nothing beneath it, turning two
    trays that each sit flat on what is below them into one part with an
    unsupported overhang. Stacked neighbours stay separate on purpose.
    """
    by_layer: dict[tuple[float, float], list[Void]] = {}
    for void in voids:
        if void.path is not None:
            by_layer.setdefault((void.position[2], void.size[2]), []).append(void)
            continue
        key = (round(void.position[2], 4), round(void.size[2], 4))
        by_layer.setdefault(key, []).append(void)

    merged: list[Void] = []
    for (z_origin, z_size), layer in sorted(by_layer.items()):
        for group in _components(layer):
            if len(group) == 1:
                merged.append(group[0])
                continue
            outline = union_outline(group)
            if not outline:
                merged.extend(group)
                continue
            xs = [x for x, _ in outline]
            ys = [y for _, y in outline]
            merged.append(
                Void(
                    position=(min(xs), min(ys), z_origin),
                    size=(max(xs) - min(xs), max(ys) - min(ys), z_size),
                    path=outline,
                )
            )
    return merged


# ------------------------------------------------------------------ assemble


def apply_clearance(void: Void, slack: float) -> Void:
    """Shrink a void by `slack` on every side so the tray can be lifted out.

    The sweep measures the true empty volume; a tray printed to that exact size
    is an interference fit against its neighbours (FR-014c). Height is left
    alone — a tray is lifted straight up, so only the footprint needs the gap.
    """
    if slack <= 0:
        return void

    if void.path is not None:
        return _inset_polygon_void(void, slack)

    return Void(
        position=(void.position[0] + slack, void.position[1] + slack, void.position[2]),
        size=(
            max(void.size[0] - 2 * slack, 0.0),
            max(void.size[1] - 2 * slack, 0.0),
            void.size[2],
        ),
    )


def _inset_polygon_void(void: Void, slack: float) -> Void:
    """Pull an L/T/U footprint inward by `slack` on every side."""
    from pyboxbuilder.paths import bounds, inset_rectilinear

    assert void.path is not None
    moved = inset_rectilinear(void.path, slack)
    (min_x, min_y), (max_x, max_y) = bounds(moved)
    return Void(
        position=(min_x, min_y, void.position[2]),
        size=(max_x - min_x, max_y - min_y, void.size[2]),
        path=moved,
    )


def generate_spacer_voids(
    container,
    placements,
    *,
    clearance: float = 0.0,
    min_dim: float = MIN_SPACER_DIM,
) -> list[Void]:
    """Sweep, merge, shrink and filter — the whole spacer pass.

    Args:
        container: (width, length, height) of the volume to fill.
        placements: The sub-boxes already placed in it.
        clearance: Slack removed from each side of a tray's footprint.
        min_dim: Trays thinner than this on any axis are dropped as unprintable.

    Returns:
        The voids that earn a tray, in descending volume.
    """
    voids = merge_voids(sweep_free_space(container, placements))
    # Drop the unprintable slivers before grouping, so a 2mm shard cannot become
    # the thin arm of an L that then has to be printed.
    printable = [v for v in voids if v.thinnest() >= min_dim - EPSILON]
    trays = [apply_clearance(v, clearance) for v in merge_rectilinear(printable)]
    kept = [v for v in trays if v.size[2] >= min_dim - EPSILON and v.volume > 0]
    return sorted(kept, key=lambda v: (-v.volume, v.position))


def generate_spacer_placements(
    container,
    placements,
    *,
    clearance: float = 0.0,
    min_dim: float = MIN_SPACER_DIM,
) -> list:
    """`generate_spacer_voids` as `Placement`s named `spacer_1..spacer_N`."""
    from pyboxbuilder.packing.layout import Placement

    return [
        Placement(
            label=f"spacer_{n}",
            position=void.position,
            size=void.size,
            rotation=False,
            path=void.relative_path(),
        )
        for n, void in enumerate(
            generate_spacer_voids(
                container, placements, clearance=clearance, min_dim=min_dim
            ),
            start=1,
        )
    ]


# --------------------------------------------------------- row-based (legacy)


def generate_spacers(
    container_width: float,
    container_length: float,
    row_widths: list[float],
    row_lengths: list[float],
    gap_threshold: float = 10.0,
    min_spacer_dim: float = 15.0,
    min_spacer_height: float = 5.0,
) -> list[SpacerSpec]:
    """Generate spacer tray specs for gaps left at the end of 2D rows.

    Predates the 3D sweep above and only sees row widths, not real placements.
    Kept for callers that lay out in rows rather than packing in 3D.

    Args:
        container_width: Outer container interior width.
        container_length: Outer container interior length.
        row_widths: Total width used by each row.
        row_lengths: Length of each row.
        gap_threshold: Gaps < this are absorbed, not filled.
        min_spacer_dim: Minimum spacer width/length before absorption.
        min_spacer_height: Default spacer tray height.

    Returns:
        List of SpacerSpec for gaps that need filling.
    """
    spacers: list[SpacerSpec] = []
    counter = 1

    for i, (row_w, row_l) in enumerate(zip(row_widths, row_lengths)):
        remaining_w = container_width - row_w
        if remaining_w >= min_spacer_dim and remaining_w >= gap_threshold:
            y_offset = sum(row_lengths[:i]) if i > 0 else 0.0
            spacers.append(
                SpacerSpec(
                    label=f"spacer_{counter}",
                    width=remaining_w,
                    length=row_l,
                    height=min_spacer_height,
                    position=(row_w, y_offset, 0),
                )
            )
            counter += 1

    # Check for gap after last row
    total_length_used = sum(row_lengths)
    remaining_l = container_length - total_length_used
    if remaining_l >= min_spacer_dim and remaining_l >= gap_threshold:
        spacers.append(
            SpacerSpec(
                label=f"spacer_{counter}",
                width=container_width,
                length=remaining_l,
                height=min_spacer_height,
                position=(0, total_length_used, 0),
            )
        )

    return spacers
