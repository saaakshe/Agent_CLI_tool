from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table


console = Console()


def print_status(payload: dict[str, Any]) -> None:
    if payload.get("running"):
        uptime = payload.get("uptime_seconds")
        status = f"[green]running[/green] on PID {payload.get('pid')}"
        if uptime is not None:
            status += f" for {uptime:.1f}s"
    else:
        status = "[yellow]stopped[/yellow]"
    console.print(Panel(status, title="Agent Status"))


def print_answer(payload: dict[str, Any]) -> None:
    answer = payload.get("answer", "").strip() or "No response received."
    console.print(Panel(answer, title="Answer", border_style="cyan"))
    notes = payload.get("notes")
    if notes:
        console.print(f"[dim]{notes}[/dim]")


def print_diff_preview(payload: dict[str, Any]) -> None:
    if payload.get("status") == "error":
        console.print(Panel(payload.get("message", "Unknown error"), title="Edit Error", border_style="red"))
        return
    diff_text = payload.get("diff", "").strip()
    if not diff_text:
        console.print(Panel("No changes were generated.", title="Diff Preview", border_style="yellow"))
        return
    console.print(Panel(Syntax(diff_text, "diff", theme="ansi_dark", word_wrap=True), title="Diff Preview"))
    summary = payload.get("summary")
    if summary:
        console.print(f"[dim]{summary}[/dim]")


def print_edit_result(payload: dict[str, Any]) -> None:
    if payload.get("status") == "applied":
        console.print(Panel(payload.get("message", "Changes applied."), title="Edit Applied", border_style="green"))
        if payload.get("diff"):
            console.print(Syntax(payload["diff"], "diff", theme="ansi_dark", word_wrap=True))
    else:
        print_diff_preview(payload)


def print_history(payload: dict[str, Any]) -> None:
    records = payload.get("history", [])
    if not records:
        console.print(Panel("No history recorded yet.", title="History"))
        return
    table = Table(title="Session History")
    table.add_column("When", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Summary")
    for item in records:
        table.add_row(item.get("timestamp", ""), item.get("kind", ""), item.get("summary", ""))
    console.print(table)
