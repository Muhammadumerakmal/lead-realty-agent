"""Input guardrail — Task 4: refuse before you pay.

This runs *before* the first model call. It is pure pattern matching — no network,
no model, no ``await`` on anything slow — so a message asking us to misrepresent a
property is rejected instantly and for zero tokens.

It targets misrepresentation only (concealing known issues, inflating
measurements, promising unapproved prices, extracting the seller's private floor,
prompt-injection). Ordinary budget and price questions pass straight through.
"""

from __future__ import annotations

import re
from typing import Any

from agents import GuardrailFunctionOutput, RunContextWrapper, TResponseInputItem, input_guardrail

_MISREP_PATTERNS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE)
    for p in (
        # conceal a known problem
        r"\b(hide|conceal|cover up|don'?t (?:mention|tell|disclose|bring up)|leave out|omit|"
        r"do not disclose|keep .{0,20}quiet)\b.{0,50}\b(defect|issue|problem|fault|damage|leak|"
        r"seepage|crack|flaw|repair|renovation|water)\b",
        r"\b(defect|issue|problem|fault|damage|leak|seepage|crack|flaw)\b.{0,50}\b(hide|conceal|"
        r"cover up|don'?t (?:mention|tell|disclose)|keep .{0,20}quiet|off the (?:report|listing))\b",
        # inflate a measurement
        r"\b(inflate|exaggerate|overstate|pad|bump up|round up|fake|invent|make up|add \d)\b.{0,50}\b"
        r"(square (?:footage|feet|foot|ft)|sq\.? ?ft|footage|area|size|marla|kanal|covered area)\b",
        r"\b(square (?:footage|feet|foot|ft)|sq\.? ?ft|footage|covered area|size|marla|kanal)\b.{0,50}\b"
        r"(inflate|exaggerate|overstate|bigger than it|more than it (?:is|really)|pad)\b",
        # promise a price the seller has not approved
        r"\b(promise|guarantee|commit to|lock in|assure (?:them|him|her|the buyer))\b.{0,50}\bprice\b",
        r"\bprice\b.{0,40}\b(seller|owner)\b.{0,25}\b(hasn'?t|has not|didn'?t|did not|never)\b.{0,20}\bapprov",
        # extract the seller's private floor
        r"\b(lowest|minimum|least|rock[- ]?bottom|bottom line)\b.{0,40}\b(seller|owner)\b.{0,25}"
        r"\b(?:will|would|can|could|to)?\s*(go|accept|take|drop|come down)\b",
        r"\b(seller'?s|owner'?s)\b.{0,20}\b(minimum|lowest|floor|bottom line|walk[- ]?away price)\b",
        r"\bwhat'?s the lowest\b.{0,30}\b(seller|owner|they|he|she)\b.{0,20}\b(accept|go|take)\b",
        # prompt injection
        r"\bignore\b.{0,25}\b(your|previous|all|the|any)\b.{0,15}\binstructions?\b",
        r"\bdisregard\b.{0,25}\b(your|previous|the)?\s*instructions?\b",
    )
]


def _collect_text(user_input: str | list[TResponseInputItem]) -> str:
    """Flatten the guardrail's input (string or message list) into one string."""
    if isinstance(user_input, str):
        return user_input
    chunks: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, str):
            chunks.append(node)
        elif isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, (list, tuple)):
            for item in node:
                walk(item)

    walk(user_input)
    return " ".join(chunks)


def scan_for_misrepresentation(text: str) -> str | None:
    """Return the first offending phrase found, or None. Plain function so it is unit-testable."""
    for pattern in _MISREP_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(0)
    return None


@input_guardrail
def no_misrepresentation(
    context: RunContextWrapper[Any],
    agent: Any,
    user_input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    """Trip the wire if the inquiry asks us to misrepresent a property. No model call."""
    hit = scan_for_misrepresentation(_collect_text(user_input))
    return GuardrailFunctionOutput(
        output_info={"matched_phrase": hit},
        tripwire_triggered=hit is not None,
    )
