from __future__ import annotations


class ValidatorAgent:
    def validate_edit(self, original: str, updated: str) -> dict[str, object]:
        if updated == original:
            return {"ok": True, "has_changes": False, "summary": "No changes were generated."}
        if not updated.strip():
            return {"ok": False, "has_changes": False, "summary": "Generated file was empty."}
        return {"ok": True, "has_changes": True, "summary": "Generated update passed basic validation."}
