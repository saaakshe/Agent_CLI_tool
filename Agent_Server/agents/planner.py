from __future__ import annotations

from Agent_Server.tools.context_loader import load_query_context, load_related_context


class PlannerAgent:
    def plan_edit(self, file_path: str, instruction: str) -> dict[str, object]:
        return {
            "goal": instruction,
            "target_file": file_path,
            "related_context": load_related_context(file_path),
            "mode": "edit",
        }

    def plan_question(self, query: str) -> dict[str, object]:
        return {
            "goal": query,
            "context": load_query_context(),
            "mode": "ask",
        }
