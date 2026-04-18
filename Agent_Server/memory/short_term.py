from __future__ import annotations

from collections import deque
from typing import Any

from config import SHORT_TERM_LIMIT


class ShortTermMemory:
    def __init__(self, limit: int = SHORT_TERM_LIMIT) -> None:
        self._items: deque[dict[str, Any]] = deque(maxlen=limit)

    def add(self, item: dict[str, Any]) -> None:
        self._items.append(item)

    def list(self) -> list[dict[str, Any]]:
        return list(self._items)
