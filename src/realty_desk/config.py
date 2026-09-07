"""Model wiring — Task 0.

The Agents SDK talks OpenAI's wire format. Gemini exposes an OpenAI-compatible
endpoint, so we point an ``AsyncOpenAI`` client at it and hand that to
``OpenAIChatCompletionsModel``. The key is read from a git-ignored ``.env``.
"""

from __future__ import annotations

import os

from agents import OpenAIChatCompletionsModel, set_tracing_disabled
from dotenv import load_dotenv
from openai import AsyncOpenAI

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
MODEL_NAME = "gemini-2.5-flash"


def get_model() -> OpenAIChatCompletionsModel:
    """Build the Gemini-backed chat model, or exit with a message (not a traceback)."""
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit(
            "GEMINI_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    # Tracing uploads run data to the OpenAI platform; we have no key for that and
    # do not need it here.
    set_tracing_disabled(True)

    client = AsyncOpenAI(api_key=api_key, base_url=GEMINI_BASE_URL)
    return OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client)
