from __future__ import annotations

from typing import Any

from Agent_Server.agents.executor import ExecutorAgent
from Agent_Server.agents.planner import PlannerAgent
from Agent_Server.agents.validator import ValidatorAgent
from Agent_Server.memory import PersistentMemory, ShortTermMemory
from Agent_Server.tools.diff import generate_diff
from Agent_Server.tools.file_ops import read_text, write_text


class AgentWorkflow:
    def __init__(self) -> None:
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.validator = ValidatorAgent()
        self.short_term = ShortTermMemory()
        self.memory = PersistentMemory()

    def ask(self, query: str) -> dict[str, Any]:
        plan = self.planner.plan_question(query)
        recalled = self.memory.recall(query)
        answer, notes = self.executor.answer_question(plan, recalled)
        record = self.memory.add_record("ask", query, {"notes": notes})
        self.short_term.add(record)
        return {"answer": answer, "notes": notes}

    def preview_edit(self, file_path: str, instruction: str) -> dict[str, Any]:
        original = read_text(file_path)
        plan = self.planner.plan_edit(file_path, instruction)
        updated, notes = self.executor.rewrite_file(file_path, instruction, plan)
        validation = self.validator.validate_edit(original, updated)
        if not validation["ok"]:
            return {"status": "error", "message": validation["summary"], "has_changes": False}
        diff_text = generate_diff(original, updated, file_path)
        return {
            "status": "preview",
            "has_changes": validation["has_changes"],
            "summary": notes if validation["has_changes"] else validation["summary"],
            "diff": diff_text,
            "updated_content": updated,
        }

    def apply_edit(self, file_path: str, instruction: str) -> dict[str, Any]:
        preview = self.preview_edit(file_path, instruction)
        if preview.get("status") == "error" or not preview.get("has_changes"):
            return preview
        write_text(file_path, preview["updated_content"])
        record = self.memory.add_record("edit", instruction, {"file_path": file_path})
        self.short_term.add(record)
        return {
            "status": "applied",
            "message": f"Applied changes to {file_path}.",
            "diff": preview["diff"],
        }

    def history(self) -> dict[str, Any]:
        return {"history": self.memory.history()}
