"""Audit trail — Task 5, option C.

``AuditHooks`` is a run-level lifecycle listener. ``on_tool_start`` /
``on_tool_end`` fire around every tool call the agent loop makes, so printing
from them gives the tool calls in true firing order with their results.

The SDK does not hand tool *arguments* to ``on_tool_start``, so each tool also
calls :func:`audit_args` on entry. That line prints only while auditing is armed
(``set_audit(True)``), which ``main`` does just for the Task 5 demo run.

What the order shows: the model and the tools take strict turns —
model -> tool -> model -> tool -> model -> final ``LeadTriage``. Tools are
resolved one at a time, each time the model asks for one; they are not gathered
up front. The loop only ends when the model emits the typed output instead of
another tool call.
"""

from __future__ import annotations

from typing import Any

from agents import RunContextWrapper, RunHooks

_AUDIT_ON = False


def set_audit(on: bool) -> None:
    """Arm or disarm the per-tool argument logging in :func:`audit_args`."""
    global _AUDIT_ON
    _AUDIT_ON = on


def audit_args(tool_name: str, **kwargs: Any) -> None:
    """Print a tool's call arguments, but only while auditing is armed."""
    if not _AUDIT_ON:
        return
    rendered = ", ".join(f"{key}={value!r}" for key, value in kwargs.items())
    print(f"      args: {rendered}")


class AuditHooks(RunHooks):
    """Logs every tool call (order + result) as the agent loop fires them."""

    def __init__(self) -> None:
        self._seq = 0
        self._open: list[tuple[int, str]] = []  # calls started, not yet ended (request order)

    async def on_tool_start(self, context: RunContextWrapper[Any], agent: Any, tool: Any) -> None:
        self._seq += 1
        self._open.append((self._seq, tool.name))
        print(f"  #{self._seq} -> {tool.name}")

    async def on_tool_end(
        self, context: RunContextWrapper[Any], agent: Any, tool: Any, result: Any
    ) -> None:
        seq, name = self._open.pop(0) if self._open else (self._seq, tool.name)
        one_line = " ".join(str(result).split())
        if len(one_line) > 140:
            one_line = one_line[:137] + "..."
        print(f"  #{seq} <- {name}  result={one_line!r}")
