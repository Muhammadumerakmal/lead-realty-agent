"""Shared Rich console + small formatting helpers.

Only the presentation layer imports this. The logic modules (config, context,
schemas, tools, guardrails, agent) stay output-free; ``saving`` and ``hooks``
print through this console so the whole demo has one consistent style.
"""

from __future__ import annotations

import sys

from rich.console import Console

# Rich renders to whatever encoding the stream reports; a piped/redirected stream
# on Windows is often cp1252 and would choke on box-drawing. Force UTF-8 first.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

console = Console()

# priority -> Rich style
PRIORITY_STYLE = {"high": "bold green", "medium": "yellow", "low": "dim"}


def priority_tag(priority: str) -> str:
    """'[bold green]HIGH[/]' etc. for inline use in console markup."""
    style = PRIORITY_STYLE.get(priority, "white")
    return f"[{style}]{priority.upper()}[/]"


def pkr(amount: int | None) -> str:
    """'PKR 5,500,000' or 'PKR -' when the client stated no number."""
    return f"PKR {amount:,}" if amount is not None else "PKR -"
