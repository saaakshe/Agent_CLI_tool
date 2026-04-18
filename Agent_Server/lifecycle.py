from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import httpx

from config import DAEMON_START_TIMEOUT, DAEMON_URL, PID_FILE_PATH


def _read_pid() -> int | None:
    if not PID_FILE_PATH.exists():
        return None
    try:
        return int(PID_FILE_PATH.read_text(encoding="utf-8").strip())
    except ValueError:
        PID_FILE_PATH.unlink(missing_ok=True)
        return None


def _pid_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def status_snapshot() -> dict[str, Any]:
    pid = _read_pid()
    if not pid or not _pid_running(pid):
        PID_FILE_PATH.unlink(missing_ok=True)
        return {"running": False, "pid": None}
    started_at = PID_FILE_PATH.stat().st_mtime
    return {"running": True, "pid": pid, "uptime_seconds": time.time() - started_at}


def _wait_for_health(timeout: float = DAEMON_START_TIMEOUT) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with httpx.Client(timeout=1.0) as client:
                response = client.get(f"{DAEMON_URL}/health")
                response.raise_for_status()
                return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError("Daemon started but did not become healthy in time.")


def start_daemon() -> dict[str, Any]:
    current = status_snapshot()
    if current["running"]:
        return current
    PID_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen(
        [sys.executable, "-m", "Agent_Server.daemon"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
        cwd=str(Path(__file__).resolve().parents[1]),
    )
    PID_FILE_PATH.write_text(str(process.pid), encoding="utf-8")
    _wait_for_health()
    return status_snapshot()


def stop_daemon() -> dict[str, Any]:
    pid = _read_pid()
    if not pid or not _pid_running(pid):
        PID_FILE_PATH.unlink(missing_ok=True)
        return {"running": False, "pid": None}
    os.kill(pid, signal.SIGTERM)
    deadline = time.time() + 5
    while time.time() < deadline:
        if not _pid_running(pid):
            PID_FILE_PATH.unlink(missing_ok=True)
            return {"running": False, "pid": None}
        time.sleep(0.2)
    PID_FILE_PATH.unlink(missing_ok=True)
    return {"running": False, "pid": None}


def restart_daemon() -> dict[str, Any]:
    stop_daemon()
    return start_daemon()
