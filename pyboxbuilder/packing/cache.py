# SPDX-License-Identifier: Apache-2.0
"""Two-level layout cache — memory + disk JSON with SHA-256 hash keys."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

CACHE_FILE = Path("pyboxbuilder/.layout_cache.json")
"""Disk cache file path."""

BGTK_VERSION = "1.0.0"
"""Version key for global cache invalidation on library changes."""

_memory_cache: dict[str, Any] = {}
"""In-memory cache for instant re-access within a process."""


def cache_key(input_data: dict[str, Any]) -> str:
    """Generate a SHA-256 hash cache key from serialized input.

    Args:
        input_data: Dictionary of input parameters to hash.

    Returns:
        Hex-encoded SHA-256 hash string.
    """
    input_data = dict(input_data)
    input_data["bgtk_version"] = BGTK_VERSION
    serialized = json.dumps(input_data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()


def load_cache() -> dict[str, Any]:
    """Load the disk cache into memory.

    Returns:
        The full cache dictionary. Empty dict if file doesn't exist.
    """
    if not CACHE_FILE.exists():
        return {}
    try:
        with open(CACHE_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # Corrupted cache file — silently overwritten
        return {}


def save_cache(cache: dict[str, Any]) -> None:
    """Save the cache dictionary to disk.

    Args:
        cache: The full cache dictionary to persist.
    """
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2, sort_keys=True)


def get_cached(key: str) -> Any | None:
    """Get a cached value by key.

    Checks memory cache first, then disk cache. Caches to memory on disk hit.

    Args:
        key: SHA-256 hash key.

    Returns:
        The cached value, or None if not found.
    """
    global _memory_cache
    if key in _memory_cache:
        return _memory_cache[key]

    disk_cache = load_cache()
    if key in disk_cache:
        _memory_cache[key] = disk_cache[key]
        return disk_cache[key]

    return None


def set_cached(key: str, value: Any) -> None:
    """Store a value in both memory and disk cache.

    Args:
        key: SHA-256 hash key.
        value: The value to cache (must be JSON-serializable).
    """
    global _memory_cache
    _memory_cache[key] = value

    disk_cache = load_cache()
    disk_cache[key] = value
    save_cache(disk_cache)


def layout_cache_clear() -> None:
    """Clear all caches (memory and disk)."""
    global _memory_cache
    _memory_cache.clear()
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
