"""The typed verdict — Task 3.

``Agent(output_type=LeadTriage)`` makes the SDK coerce the model's reply into
this class. Once it is a typed object, ``triage.priority == "high"`` and
``triage.budget_pkr * 1.05`` are ordinary Python — the program acts on fields,
not on a paragraph.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Intent = Literal["buy", "rent", "sell", "browsing"]
Priority = Literal["high", "medium", "low"]


class LeadTriage(BaseModel):
    """Structured triage of a single inbound inquiry."""

    intent: Intent = Field(description="What the client wants: buy, rent, sell, or just browsing.")
    budget_pkr: int | None = Field(
        default=None,
        description="Stated budget in PKR as a whole number, or null if the client gave none.",
    )
    red_flags: list[str] = Field(
        default_factory=list,
        description=(
            "Short phrases for anything that makes this lead risky or not worth a callback: "
            "lowball offer, no budget, unrealistic timeline, no area, time-waster language, etc."
        ),
    )
    priority: Priority = Field(
        description="high = call within the hour; medium = follow up; low = park it."
    )
    suggested_reply: str = Field(description="One short reply the agent could send as-is.")
