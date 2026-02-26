from __future__ import annotations

import time
from dataclasses import dataclass
from threading import Lock
from typing import Any


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class InMemoryTTLCache:
    def __init__(self):
        self._lock = Lock()
        self._store: dict[str, CacheEntry] = {}

    def get(self, key: str) -> Any | None:
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return None
            if time.time() >= item.expires_at:
                self._store.pop(key, None)
                return None
            return item.value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        with self._lock:
            self._store[key] = CacheEntry(value=value, expires_at=time.time() + ttl_seconds)
