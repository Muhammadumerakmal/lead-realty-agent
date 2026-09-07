"""Web UI — a thin FastAPI layer over the same triage agent.

    uv run realty-desk-web       # then open http://127.0.0.1:8000

The page POSTs a raw inquiry to ``/api/triage``; the server runs the guardrail
and (if it passes) the triage agent, applies the same code-side save decision as
the CLI, and returns the typed verdict as JSON. No agent logic lives here.
"""

from __future__ import annotations

import json
from pathlib import Path

from agents import InputGuardrailTripwireTriggered, Runner
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from realty_desk.agent import build_triage_agent
from realty_desk.config import active_model_label, get_model
from realty_desk.context import sample_agency
from realty_desk.saving import SAVED_PATH, decide_and_save
from realty_desk.schemas import LeadTriage

_INDEX_HTML = (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")

app = FastAPI(title="Realty Desk")

_agent = None  # built on first request so a missing key is a 503, not an import crash


def _get_agent():
    global _agent
    if _agent is None:
        _agent = build_triage_agent(get_model())
    return _agent


def _read_saved() -> list[dict]:
    try:
        data = json.loads(SAVED_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


class TriageRequest(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return _INDEX_HTML


@app.get("/api/meta")
def meta() -> dict:
    return {"model": active_model_label(), "agency": sample_agency().agency_name}


@app.get("/api/saved")
def saved() -> list[dict]:
    return _read_saved()


@app.post("/api/reset")
def reset() -> dict:
    SAVED_PATH.write_text("[]\n", encoding="utf-8")
    return {"saved": []}


@app.post("/api/triage")
async def triage(req: TriageRequest) -> dict:
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message is empty.")

    try:
        agent = _get_agent()
    except SystemExit as exc:  # missing API key
        raise HTTPException(status_code=503, detail=str(exc)) from None

    try:
        result = await Runner.run(agent, message, context=sample_agency())
    except InputGuardrailTripwireTriggered as exc:
        phrase = exc.guardrail_result.output.output_info.get("matched_phrase")
        return {"declined": True, "matched_phrase": phrase, "saved": False}

    verdict: LeadTriage = result.final_output
    was_saved = decide_and_save(verdict)  # same code-side decision as the CLI
    return {"declined": False, "triage": verdict.model_dump(), "saved": was_saved}


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


if __name__ == "__main__":
    main()
