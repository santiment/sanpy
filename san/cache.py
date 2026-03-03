"""Simple TTL cache for metadata queries."""

import time
from typing import Any


class TTLCache:
    """Dict-like cache where entries expire after *ttl* seconds."""

    def __init__(self, ttl: float = 300.0) -> None:
        self.ttl = ttl
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        ts, value = entry
        if time.monotonic() - ts > self.ttl:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.monotonic(), value)

    def clear(self) -> None:
        self._store.clear()


_metadata_cache = TTLCache(ttl=300.0)


def clear_cache() -> None:
    """Clear all cached metadata."""
    _metadata_cache.clear()
