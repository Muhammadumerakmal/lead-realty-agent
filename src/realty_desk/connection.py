"""Task 0 — the bare connectivity check.

A plain agent, no tools, no structured output: just enough to prove the key
loads, the Gemini endpoint answers, and the async runner works end to end.
"""

from __future__ import annotations

from agents import Agent, OpenAIChatCompletionsModel

HARDCODED_MESSAGE = (
    "Hi, I saw a 5 marla house listed in Bahria Town Lahore. Is it still available "
    "and can I visit this weekend?"
)


def build_connection_agent(model: OpenAIChatCompletionsModel) -> Agent:
    return Agent(
        name="Realty Desk",
        instructions=(
            "You are a real estate agency front desk. Reply to the client in two or "
            "three sentences, politely and concretely."
        ),
        model=model,
    )
