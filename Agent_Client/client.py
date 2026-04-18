from __future__ import annotations

import time
from typing import Any

import httpx

from Agent_Server.lifecycle import start_daemon, status_snapshot
from config import DAEMON_START_TIMEOUT, DAEMON_URL


class AgentClient:
    def __init__(self, base_url: str = DAEMON_URL, timeout: float = 120.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        auto_start: bool = True,
    ) -> Any:
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(method, url, json=json)
                response.raise_for_status()
                return response.json()
        except (httpx.ConnectError, httpx.ReadError, httpx.RemoteProtocolError):
            if not auto_start:
                raise
            start_daemon()
            self.wait_until_ready()
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(method, url, json=json)
                response.raise_for_status()
                return response.json()

    def wait_until_ready(self, timeout: float = DAEMON_START_TIMEOUT) -> dict[str, Any]:
        deadline = time.time() + timeout
        last_error: Exception | None = None
        while time.time() < deadline:
            try:
                return self.health(auto_start=False)
            except Exception as exc:  # pragma: no cover - network timing dependent
                last_error = exc
                time.sleep(0.25)
        if last_error:
            raise RuntimeError("Daemon did not become ready in time.") from last_error
        raise RuntimeError("Daemon did not become ready in time.")

    def health(self, *, auto_start: bool = True) -> dict[str, Any]:
        return self._request("GET", "/health", auto_start=auto_start)

    def ask(self, query: str) -> dict[str, Any]:
        return self._request("POST", "/ask", json={"query": query})

    def preview_edit(self, file_path: str, instruction: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "/edit/preview",
            json={"file_path": file_path, "instruction": instruction},
        )

    def apply_edit(self, file_path: str, instruction: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "/edit/apply",
            json={"file_path": file_path, "instruction": instruction},
        )

    def history(self) -> dict[str, Any]:
        return self._request("GET", "/history")

    def shutdown(self) -> dict[str, Any]:
        return self._request("POST", "/shutdown", auto_start=False)

    def status(self) -> dict[str, Any]:
        snapshot = status_snapshot()
        if not snapshot["running"]:
            return snapshot
        try:
            health = self.health(auto_start=False)
            snapshot["health"] = health
        except Exception as exc:
            snapshot["health_error"] = str(exc)
        return snapshot
