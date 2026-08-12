# SPDX-License-Identifier: Apache-2.0
"""Immutable RGBA color dataclass with named presets."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Color:
    """RGBA color with components in 0.0–1.0 range."""

    r: float
    """Red channel (0.0–1.0)."""
    g: float
    """Green channel (0.0–1.0)."""
    b: float
    """Blue channel (0.0–1.0)."""
    a: float = 1.0
    """Alpha channel (0.0–1.0). Defaults to fully opaque."""

    @classmethod
    def WHITE(cls) -> "Color":
        """White (1, 1, 1, 1)."""
        return cls(1.0, 1.0, 1.0)

    @classmethod
    def BLACK(cls) -> "Color":
        """Black (0, 0, 0, 1)."""
        return cls(0.0, 0.0, 0.0)

    @classmethod
    def RED(cls) -> "Color":
        """Red (1, 0, 0, 1)."""
        return cls(1.0, 0.0, 0.0)

    @classmethod
    def GREEN(cls) -> "Color":
        """Green (0, 1, 0, 1)."""
        return cls(0.0, 1.0, 0.0)

    @classmethod
    def BLUE(cls) -> "Color":
        """Blue (0, 0, 1, 1)."""
        return cls(0.0, 0.0, 1.0)

    @classmethod
    def GOLD(cls) -> "Color":
        """Gold (0.9, 0.7, 0.1, 1)."""
        return cls(0.9, 0.7, 0.1)

    def __iter__(self):
        return iter((self.r, self.g, self.b, self.a))
