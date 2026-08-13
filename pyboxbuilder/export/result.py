# SPDX-License-Identifier: Apache-2.0
"""Export result data class."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExportResult:
    """Result of a Project.export() call."""

    written: tuple[str, ...]
    """Relative file paths that were created or updated."""
    skipped: tuple[str, ...]
    """Relative file paths skipped (unchanged geometry)."""
    total_files: int
    """Total files in the export tree."""
    cached_from: str | None = None
    """Cache key hash if layout was served from cache, else None."""
