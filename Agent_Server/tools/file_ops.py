from __future__ import annotations

from pathlib import Path

from config import PROJECT_ROOT


def resolve_path(file_path: str) -> Path:
    path = Path(file_path)
    if not path.is_absolute():
        path = (PROJECT_ROOT / path).resolve()
    else:
        path = path.resolve()
    try:
        path.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise ValueError(f"Refusing to access path outside project root: {path}") from exc
    return path


def read_text(file_path: str) -> str:
    path = resolve_path(file_path)
    return path.read_text(encoding="utf-8")


def write_text(file_path: str, content: str) -> Path:
    path = resolve_path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
