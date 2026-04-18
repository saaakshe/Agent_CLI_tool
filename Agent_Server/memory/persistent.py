from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import HISTORY_FILE_PATH, MEMORY_FILE_PATH, TOP_K_MEMORY

TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]+")


def _tokenize(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text)}


class PersistentMemory:
    def __init__(self, memory_path: Path = MEMORY_FILE_PATH, history_path: Path = HISTORY_FILE_PATH) -> None:
        self.memory_path = memory_path
        self.history_path = history_path
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

    def _save(self, path: Path, payload: list[dict[str, Any]]) -> None:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def add_record(self, kind: str, summary: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "kind": kind,
            "summary": summary,
            "details": details or {},
            "tokens": sorted(_tokenize(f"{kind} {summary} {json.dumps(details or {}, sort_keys=True)}")),
        }
        history = self._load(self.history_path)
        history.append(record)
        self._save(self.history_path, history)

        memory = self._load(self.memory_path)
        memory.append(record)
        self._save(self.memory_path, memory)
        return record

    def history(self) -> list[dict[str, Any]]:
        return list(reversed(self._load(self.history_path)))

    def recall(self, query: str, top_k: int = TOP_K_MEMORY) -> list[dict[str, Any]]:
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []
        scored: list[tuple[int, dict[str, Any]]] = []
        for item in self._load(self.memory_path):
            item_tokens = set(item.get("tokens", []))
            overlap = len(query_tokens & item_tokens)
            if overlap:
                scored.append((overlap, item))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored[:top_k]]
