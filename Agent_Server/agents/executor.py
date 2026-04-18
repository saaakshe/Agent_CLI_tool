from __future__ import annotations

from typing import Any

import httpx

from Agent_Server.tools.file_ops import read_text
from config import MODEL_NAME, OLLAMA_CHAT_URL, OLLAMA_TIMEOUT


class ExecutorAgent:
    def _call_ollama(self, messages: list[dict[str, str]]) -> str:
        payload = {"model": MODEL_NAME, "stream": False, "messages": messages}
        with httpx.Client(timeout=OLLAMA_TIMEOUT) as client:
            response = client.post(OLLAMA_CHAT_URL, json=payload)
            response.raise_for_status()
        data = response.json()
        message = data.get("message", {})
        content = message.get("content")
        if not content:
            raise RuntimeError("Ollama returned an empty response.")
        return content

    def answer_question(self, plan: dict[str, Any], memory: list[dict[str, Any]]) -> tuple[str, str]:
        context_chunks = []
        for item in plan.get("context", [])[:4]:
            context_chunks.append(f"File: {item['path']}\n{item['content']}")
        memory_chunks = []
        for item in memory[:4]:
            memory_chunks.append(f"{item['timestamp']} {item['kind']}: {item['summary']}")

        system_prompt = (
            "You are a local coding assistant. Answer using the provided repository context and memory. "
            "If context is insufficient, say so plainly and offer the best grounded summary you can."
        )
        user_prompt = (
            f"Question:\n{plan['goal']}\n\n"
            f"Relevant code context:\n\n{'\n\n'.join(context_chunks) or 'No code context.'}\n\n"
            f"Relevant memory:\n\n{'\n'.join(memory_chunks) or 'No memory matches.'}"
        )
        try:
            answer = self._call_ollama(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
            )
            return answer, "Answered using Ollama."
        except Exception:
            fallback = "I couldn't reach the local Ollama model, so this answer is a repository-grounded fallback.\n\n"
            if context_chunks:
                fallback += "I found these likely relevant files:\n"
                fallback += "\n".join(f"- {item['path']}" for item in plan.get("context", [])[:4])
            else:
                fallback += "I don't have enough code context loaded yet to answer confidently."
            if memory_chunks:
                fallback += "\n\nRelated past memory:\n" + "\n".join(f"- {chunk}" for chunk in memory_chunks)
            return fallback, "Fallback answer generated because Ollama was unavailable."

    def rewrite_file(self, file_path: str, instruction: str, plan: dict[str, Any]) -> tuple[str, str]:
        original = read_text(file_path)
        related = []
        for item in plan.get("related_context", [])[:3]:
            related.append(f"Related file: {item['path']}\n{item['content']}")
        system_prompt = (
            "You are a careful code editor. Return only the full updated file contents with no markdown fences, "
            "no explanation, and preserve unrelated code."
        )
        user_prompt = (
            f"Target file path: {file_path}\n\n"
            f"Instruction:\n{instruction}\n\n"
            f"Current file contents:\n{original}\n\n"
            f"Related context:\n\n{'\n\n'.join(related) or 'No additional context.'}"
        )
        try:
            updated = self._call_ollama(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
            )
            return updated.rstrip() + ("\n" if original.endswith("\n") else ""), "Edit generated using Ollama."
        except Exception as exc:
            raise RuntimeError(
                "Could not generate an edit because the local Ollama model is unavailable. "
                "Start Ollama and ensure the configured model is installed."
            ) from exc
