# SPDX-License-Identifier: Apache-2.0
"""Polygon helpers for the rectilinear outlines the packer produces.

Leftover space between axis-aligned boxes is always rectilinear — every edge
runs along X or Y — which makes exact offsetting a few lines of arithmetic
rather than a job for a general polygon-offset library. Both the spacer pass
(clearance around a tray) and `PathBox` (a tray's inner cavity) need it.
"""

from __future__ import annotations

from typing import Sequence

EPSILON = 0.01

Point = tuple[float, float]
Path = tuple[Point, ...]


def polygon_area(path: Sequence[Point]) -> float:
    """Shoelace area of a closed outline."""
    return abs(signed_area(path)) / 2


def signed_area(path: Sequence[Point]) -> float:
    """Twice the signed area — positive when the outline runs counter-clockwise."""
    total = 0.0
    for i, (x0, y0) in enumerate(path):
        x1, y1 = path[(i + 1) % len(path)]
        total += x0 * y1 - x1 * y0
    return total


def is_rectilinear(path: Sequence[Point]) -> bool:
    """True when every edge is axis-aligned."""
    for i, (x0, y0) in enumerate(path):
        x1, y1 = path[(i + 1) % len(path)]
        if abs(x0 - x1) > EPSILON and abs(y0 - y1) > EPSILON:
            return False
    return True


def inset_rectilinear(path: Sequence[Point], distance: float) -> Path:
    """Pull a rectilinear outline inward by `distance`.

    Every corner joins one horizontal and one vertical edge, so its new position
    is the old one moved by `distance` along each incident edge's inward normal.
    That is exact for convex and reflex corners alike — an L stays an L, with all
    six of its sides moved in, which a centroid scale would not manage. A reflex
    corner correctly moves *out* into the notch, keeping the arm's width right.

    Which way is inward depends on the direction the outline is traversed, not on
    where a corner's neighbours happen to sit, so the normals come from the
    directed edges: for a counter-clockwise ring, edge `(dx, dy)` points inward
    along `(-dy, dx)`.

    Args:
        path: A closed rectilinear outline.
        distance: How far to move each edge inward. Negative grows the outline.

    Returns:
        The inset outline, with the same number of points.
    """
    if distance == 0 or len(path) < 4:
        return tuple(path)

    winding = 1.0 if signed_area(path) > 0 else -1.0
    count = len(path)

    moved: list[Point] = []
    for n, point in enumerate(path):
        incoming = (path[n - 1], point)
        outgoing = (point, path[(n + 1) % count])

        shift_x = shift_y = 0.0
        for (ax, ay), (bx, by) in (incoming, outgoing):
            edge_x, edge_y = bx - ax, by - ay
            # Axis-aligned, so exactly one component of the normal is non-zero.
            shift_x += -edge_y * winding
            shift_y += edge_x * winding

        moved.append((
            point[0] + distance * _sign(shift_x),
            point[1] + distance * _sign(shift_y),
        ))
    return tuple(moved)


def bounds(path: Sequence[Point]) -> tuple[Point, Point]:
    """(min corner, max corner) of an outline."""
    xs = [x for x, _ in path]
    ys = [y for _, y in path]
    return ((min(xs), min(ys)), (max(xs), max(ys)))


def _sign(value: float) -> float:
    if value > EPSILON:
        return 1.0
    if value < -EPSILON:
        return -1.0
    return 0.0
