"""The save decision — Task 3.

The model never gets a save tool. It returns a :class:`LeadTriage`; this module's
Python decides, by reading ``triage.priority``, whether the lead is worth a
callback and therefore worth persisting to ``saved.json``.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from realty_desk.schemas import LeadTriage

# Project root holds saved.json regardless of the caller's working directory.
SAVED_PATH = Path(__file__).resolve().parents[2] / "saved.json"

# The one knob the "amendment" band is likely to turn.
SAVE_WHEN_PRIORITY = "high"


def save_lead(triage: LeadTriage, lead_id: str | None = None, path: Path = SAVED_PATH) -> None:
    """Append one triaged lead to the JSON list at ``path`` (creating it if needed)."""
    try:
        existing = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(existing, list):
            existing = []
    except (FileNotFoundError, json.JSONDecodeError):
        existing = []

    record = triage.model_dump()
    record["lead_id"] = lead_id
    record["saved_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    existing.append(record)
    path.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def decide_and_save(triage: LeadTriage, lead_id: str | None = None) -> bool:
    """Our code — not the model — decides. Returns True if the lead was saved.

    Prints a one-line banner (priority + budget) before saving, and does a bit of
    arithmetic on ``budget_pkr`` to prove it is a real integer, not text.
    """
    if triage.priority != SAVE_WHEN_PRIORITY:
        return False

    budget = triage.budget_pkr or 0
    outreach_ceiling = int(budget * 1.05)  # arithmetic on an int field
    print(
        f"[SAVE] priority={triage.priority} budget_pkr={budget:,} "
        f"(callback ceiling +5% = PKR {outreach_ceiling:,})"
    )
    save_lead(triage, lead_id=lead_id)
    return True
