from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from Agent_Server.router import attach_routes
from config import DAEMON_HOST, DAEMON_PORT


def create_app() -> FastAPI:
    app = FastAPI(title="Local Agentic CLI Daemon")
    attach_routes(app)
    return app


app = create_app()


def main() -> None:
    uvicorn.run("Agent_Server.daemon:app", host=DAEMON_HOST, port=DAEMON_PORT, log_level="warning")


if __name__ == "__main__":
    main()
