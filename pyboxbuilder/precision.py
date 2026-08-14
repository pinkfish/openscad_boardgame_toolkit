# SPDX-License-Identifier: Apache-2.0
"""Curve precision — the ``fn`` / ``fa`` / ``fs`` tessellation controls.

Every curved feature the toolkit builds (cylinders, spheres, fillets and
chamfers, finger scoops and holes, lid-pattern curves) takes its facet count
from the precision in force, so one setting on :meth:`Project.export` or
:meth:`Project.show` reaches all of them. No geometry call hardcodes a facet
count the caller cannot override.

The setting travels in a :class:`~contextvars.ContextVar` rather than through
every function signature: the geometry call sites are several layers below the
public API and threading a parameter through each of them would put a
precision argument on functions that have nothing else to do with it.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Iterator

#: Default minimum angle per fragment, in degrees (OpenSCAD's ``$fa``).
DEFAULT_FA = 12.0

#: Default minimum fragment size, in mm (OpenSCAD's ``$fs``).
DEFAULT_FS = 2.0


@dataclass(frozen=True)
class Precision:
    """How finely curves are tessellated.

    Mirrors OpenSCAD's three special variables. ``fn`` is absolute and wins
    when set; otherwise ``fa`` and ``fs`` together decide the facet count, so
    a small radius gets few facets and a large one gets many.
    """

    fn: int | None = None
    """Fixed number of facets per full circle. ``None`` defers to fa/fs."""
    fa: float = DEFAULT_FA
    """Minimum angle per fragment, in degrees. Lower is finer."""
    fs: float = DEFAULT_FS
    """Minimum fragment size, in mm. Lower is finer."""

    def __post_init__(self) -> None:
        """Validate the settings.

        Raises:
            ValueError: If ``fn`` is set below 3 (fewer than three facets is
                not a curve), or if ``fa``/``fs`` is not positive.
        """
        if self.fn is not None and self.fn < 3:
            raise ValueError(f"fn must be >= 3 when set; got {self.fn}")
        if self.fa <= 0:
            raise ValueError(f"fa must be > 0; got {self.fa}")
        if self.fs <= 0:
            raise ValueError(f"fs must be > 0; got {self.fs}")

    def kwargs(self) -> dict[str, float | int]:
        """Return the settings as keyword arguments for a pybosl2 call.

        Returns:
            A dict carrying ``fa``/``fs``, plus ``fn`` when it is set. Splat
            it into any curve-producing constructor:
            ``cylinder(height=h, radius=r, **precision().kwargs())``.
        """
        values: dict[str, float | int] = {"fa": self.fa, "fs": self.fs}
        if self.fn is not None:
            values["fn"] = self.fn
        return values


_CURRENT: ContextVar[Precision] = ContextVar("pyboxbuilder_precision", default=Precision())


def precision() -> Precision:
    """Return the precision currently in force.

    Returns:
        The innermost :class:`Precision` set by :func:`use`, or the default
        (``fa=12, fs=2``) outside any such block.
    """
    return _CURRENT.get()


def kwargs() -> dict[str, float | int]:
    """Shorthand for ``precision().kwargs()`` at a geometry call site.

    Returns:
        The tessellation keyword arguments for the precision in force.
    """
    return precision().kwargs()


@contextmanager
def use(
    fn: int | None = None,
    fa: float | None = None,
    fs: float | None = None,
) -> Iterator[Precision]:
    """Build geometry at a given curve precision for the duration of a block.

    Unspecified settings keep their current value, so ``use(fn=64)`` raises
    the facet count without disturbing fa/fs.

    Args:
        fn: Fixed facets per circle, or ``None`` to defer to fa/fs.
        fa: Minimum angle per fragment in degrees; ``None`` keeps the current.
        fs: Minimum fragment size in mm; ``None`` keeps the current.

    Yields:
        The :class:`Precision` in force inside the block.

    Raises:
        ValueError: If any setting is out of range (see :class:`Precision`).
    """
    base = precision()
    active = Precision(
        fn=fn if fn is not None else base.fn,
        fa=fa if fa is not None else base.fa,
        fs=fs if fs is not None else base.fs,
    )
    token = _CURRENT.set(active)
    try:
        yield active
    finally:
        _CURRENT.reset(token)
