from __future__ import annotations

from pathlib import Path

from config import PROJECT_ROOT
from Agent_Server.tools.file_ops import resolve_path


def load_related_context(file_path: str, limit: int = 4) -> list[dict[str, str]]:
    target = resolve_path(file_path)
    target_name = target.stem
    contexts: list[dict[str, str]] = []
    for candidate in PROJECT_ROOT.rglob("*.py"):
        if candidate == target or ".git" in candidate.parts or "data" in candidate.parts:
            continue
        try:
            text = candidate.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        score = 0
        if f"import {target_name}" in text or f"from {target_name} import" in text:
            score += 3
        if target.name in text:
            score += 2
        if score:
            contexts.append({"path": str(candidate.relative_to(PROJECT_ROOT)), "content": text, "score": str(score)})
    contexts.sort(key=lambda item: int(item["score"]), reverse=True)
    return contexts[:limit]


def load_query_context(limit: int = 6) -> list[dict[str, str]]:
    contexts: list[dict[str, str]] = []
    for candidate in sorted(PROJECT_ROOT.rglob("*.py"))[:limit]:
        if ".git" in candidate.parts or "data" in candidate.parts:
            continue
        try:
            text = candidate.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        contexts.append({"path": str(candidate.relative_to(PROJECT_ROOT)), "content": text[:3000]})
    return contexts
