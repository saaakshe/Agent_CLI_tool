from __future__ import annotations

import typer

from Agent_Client.client import AgentClient
from Agent_Client.renderer import print_answer, print_diff_preview, print_edit_result, print_history, print_status
from Agent_Server.lifecycle import restart_daemon, start_daemon, stop_daemon

app = typer.Typer(help="A CLI for interacting with the Agent Daemon. Use this tool to ask questions, edit files, view history, and manage the daemon's lifecycle.")


@app.command()
def ask(query: str) -> None:
    client = AgentClient()
    payload = client.ask(query)
    print_answer(payload)


@app.command()
def edit(file: str, instruction: str, dry_run: bool = typer.Option(False, "--dry-run", help="Preview only; do not write changes.")) -> None:
    client = AgentClient()
    preview = client.preview_edit(file, instruction)
    print_diff_preview(preview)
    if dry_run or preview.get("status") == "error" or not preview.get("has_changes"):
        return
    if typer.confirm("Apply these changes?", default=True):
        result = client.apply_edit(file, instruction)
        print_edit_result(result)


@app.command()
def history() -> None:
    client = AgentClient()
    payload = client.history()
    print_history(payload)


@app.command()
def start() -> None:
    payload = start_daemon()
    print_status(payload)


@app.command()
def stop() -> None:
    payload = stop_daemon()
    print_status(payload)


@app.command()
def status() -> None:
    client = AgentClient()
    payload = client.status()
    print_status(payload)


@app.command()
def restart() -> None:
    payload = restart_daemon()
    print_status(payload)


if __name__ == "__main__":
    app()
