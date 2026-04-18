from __future__ import annotations

import os
import signal
import threading
from time import time

from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel

from Agent_Server.agents.workflow import AgentWorkflow

router = APIRouter()
STARTED_AT = time()
WORKFLOW = AgentWorkflow()


class AskRequest(BaseModel):
    query: str


class EditRequest(BaseModel):
    file_path: str
    instruction: str


@router.get("/health")
def health() -> dict[str, object]:
    return {"status": "ok", "uptime_seconds": round(time() - STARTED_AT, 2)}


@router.post("/ask")
def ask(payload: AskRequest) -> dict[str, object]:
    return WORKFLOW.ask(payload.query)


@router.post("/edit/preview")
def edit_preview(payload: EditRequest) -> dict[str, object]:
    try:
        return WORKFLOW.preview_edit(payload.file_path, payload.instruction)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        return {"status": "error", "message": str(exc), "has_changes": False}


@router.post("/edit/apply")
def edit_apply(payload: EditRequest) -> dict[str, object]:
    try:
        return WORKFLOW.apply_edit(payload.file_path, payload.instruction)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        return {"status": "error", "message": str(exc), "has_changes": False}


@router.get("/history")
def history() -> dict[str, object]:
    return WORKFLOW.history()


@router.post("/shutdown")
def shutdown() -> dict[str, str]:
    threading.Timer(0.1, lambda: os.kill(os.getpid(), signal.SIGTERM)).start()
    return {"status": "stopping"}


def attach_routes(app: FastAPI) -> None:
    app.include_router(router)
