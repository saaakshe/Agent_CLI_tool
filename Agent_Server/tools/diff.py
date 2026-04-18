from __future__ import annotations

from difflib import unified_diff


def generate_diff(original: str, updated: str, file_path: str) -> str:
    return "\n".join(
        unified_diff(
            original.splitlines(),
            updated.splitlines(),
            fromfile=f"{file_path} (before)",
            tofile=f"{file_path} (after)",
            lineterm="",
        )
    )
