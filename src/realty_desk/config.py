"""Model wiring — Task 0.

The Agents SDK speaks OpenAI's wire format. This project runs on OpenAI
(``gpt-4o-mini``); put ``OPENAI_API_KEY`` in a git-ignored ``.env``.

A Gemini key is also accepted: set ``GEMINI_API_KEY`` instead and it routes to
Gemini's OpenAI-compatible endpoint with ``gemini-2.5-flash``. Whichever key is
present wins, OpenAI first.
"""

from __future__ import annotations

import os

from agents import OpenAIChatCompletionsModel, set_tracing_disabled
from dotenv import load_dotenv
from openai import AsyncOpenAI

OPENAI_MODEL = "gpt-4o-mini"  # bump to "gpt-4.1-mini" for sharper triage judgement
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def active_model_label() -> str:
    """Name of the model the next :func:`get_model` call will build (for status lines)."""
    load_dotenv()
    if os.environ.get("OPENAI_API_KEY"):
        return OPENAI_MODEL
    if os.environ.get("GEMINI_API_KEY"):
        return GEMINI_MODEL
    return "no model (missing API key)"


def get_model() -> OpenAIChatCompletionsModel:
    """Build the chat model from whichever key is set, or exit with a message (not a traceback)."""
    load_dotenv()

    # Tracing uploads run data to the OpenAI platform; not needed here.
    set_tracing_disabled(True)

    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        client = AsyncOpenAI(api_key=openai_key)
        return OpenAIChatCompletionsModel(model=OPENAI_MODEL, openai_client=client)

    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        client = AsyncOpenAI(api_key=gemini_key, base_url=GEMINI_BASE_URL)
        return OpenAIChatCompletionsModel(model=GEMINI_MODEL, openai_client=client)

    raise SystemExit(
        "No API key found. Copy .env.example to .env and set OPENAI_API_KEY (or GEMINI_API_KEY)."
    )
