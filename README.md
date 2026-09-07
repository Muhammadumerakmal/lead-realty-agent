# Realty Desk

Takes **one raw client inquiry** (WhatsApp / Zillow / portal / walk-in email),
works out what the client wants, checks it against **private** listing inventory
and agent availability through tools, and returns a **typed verdict**
(`LeadTriage`) your program can act on. The lead is saved for a callback only when
**your Python code** — not the model — decides it is worth one. Messages asking
the desk to misrepresent a property are refused with **zero model calls**.

Model: `gemini-2.5-flash` via its OpenAI-compatible endpoint, driven by the
OpenAI Agents SDK.

## Run

```bash
uv sync
cp .env.example .env          # then put your real GEMINI_API_KEY in .env
uv run realty-desk
```

One command runs an ordered, rubric-labeled demo (rendered with [Rich](https://github.com/Textualize/rich) — section rules, a triage table, a guardrail table, and a coloured audit trail):

| Section | What it shows |
| --- | --- |
| Task 0 | Key loads from `.env`, Gemini answers, async runner works — plain reply, no traceback |
| Tasks 1–3 | Triage of the 6 fixtures in `leads.json`; `lookup_listing_availability` is called before any price; serious leads print `[SAVE] …` and land in `saved.json` |
| Task 2 | `lookup_listing_availability.params_json_schema` has **no** `context` parameter; `seller_min_price_pkr` lives only in `context.py` |
| Task 4 | A misrepresentation message and an injection probe are declined in ~1 ms (no model call); an ordinary lead right after still passes |
| Task 5C | Every tool call logged in firing order with args + result |

## Layout

```
src/realty_desk/
  config.py       Gemini model wiring (Task 0); friendly exit if key missing
  context.py      AgencyProfile + Listing dataclasses; sample_agency() — PRIVATE data (Task 2)
  schemas.py      LeadTriage — the structured output type (Task 3)
  tools.py        lookup_listing_availability, check_agent_availability — read from context (Tasks 1–2)
  saving.py       decide_and_save() — the code-side callback/save decision (Task 3)
  guardrails.py   no_misrepresentation — pure-regex input guardrail, zero model calls (Task 4)
  hooks.py        AuditHooks — lifecycle logging of tool calls (Task 5C)
  agent.py        build_triage_agent() — ties tools + guardrail + output_type together
  connection.py   Task 0 bare connectivity agent
  ui.py           shared Rich console + small formatters (presentation layer only)
  main.py         the one-command demo
leads.json        6 fixtures (committed)
saved.json        starts as [] (committed)
```

## Design seams (for a late spec change)

- **Save policy** — one function: `saving.decide_and_save` / `saving.SAVE_WHEN_PRIORITY`.
- **Verdict shape** — `schemas.LeadTriage`.
- **Fixtures / agency data** — `leads.json`, `context.sample_agency()`.
- **Guardrail rules** — one pattern list in `guardrails.py`.
- **Agent's tools** — the `tools=[...]` list in `agent.build_triage_agent`.

## What the audit-trail order reveals

Each model turn asks for one or more tools; the loop runs them, feeds every result
back, and the model runs again — `model → tool(s) → model → … → LeadTriage`. It
ends only when the model returns the typed `LeadTriage` instead of another tool
call. In the trace, `->` lines that cluster before the `<-` lines mean the model
asked for those tools together in one turn; interleaved lines mean one at a time.
