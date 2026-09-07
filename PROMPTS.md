# PROMPTS.md

Every prompt sent to Claude Code, in order. The build was planned first, then
implemented in one pass, so the prompts are not one-per-task — the task headings
below are added for navigation.

## Planning

1. `@realty-desk-practice.pdf first we will plan and then make it`
2. (clarifying questions from Claude) — answers: "use the best practices" for the
   Task 5 bonus choice and run style; "also openai key too" for API keys.
3. Approved the written plan (single `main.py` demo flow; Task 5 → option C audit
   trail; Agents SDK + Gemini OpenAI-compatible endpoint).

## Task 0 — Project and connection
_Covered by the planning prompts above._ Claude ran `uv init --package realty-desk`,
added `openai-agents` / `python-dotenv` / `pydantic`, and wrote `config.py`
(Gemini via `OpenAIChatCompletionsModel`, key from `.env`, friendly `SystemExit`
if missing) and `connection.py`.

## Task 1 — Sample data and lookup tools
_Covered by the planning prompts above._ `leads.json` (6 fixtures) and `tools.py`
(`lookup_listing_availability`, `check_agent_availability`), docstrings written for
model tool-selection.

## Task 2 — Data the model is never given
_Covered by the planning prompts above._ `context.py` (`AgencyProfile` /
`Listing`, `seller_min_price_pkr` private); tools take
`RunContextWrapper[AgencyProfile]`; schema evidence printed in `main.py`.

## Task 3 — A verdict the program can act on
_Covered by the planning prompts above._ `schemas.py` (`LeadTriage`) and
`saving.py` (`decide_and_save` — Python reads `priority`, prints the banner,
appends to `saved.json`).

## Task 4 — Refusing before you pay
_Covered by the planning prompts above._ `guardrails.py` (`no_misrepresentation`,
pure regex, `@input_guardrail`), attached to the agent; `main.py` catches
`InputGuardrailTripwireTriggered`.

## Task 5 — Bonus (C: audit trail)
_Covered by the planning prompts above._ `hooks.py` (`AuditHooks` +
`audit_args`), passed to `Runner.run(hooks=...)` for one demo lead.

## Follow-ups

4. `https://github.com/Muhammadumerakmal/lead-realty-agent push here with proper
   comments` — restructured the single scaffold commit into nine task-scoped
   commits and pushed to `main`.
5. `make .env and paste this <OpenAI key>` → `Smoke-test on OpenAI, then revert` —
   the pasted key was an OpenAI key, not a Gemini one; ran the full demo against
   `gpt-4o-mini` to exercise the tool / guardrail / save / structured-output
   paths, which surfaced the Task 1 comma-match bug, then reverted `config.py` to
   Gemini-only. The committed code stays on `gemini-2.5-flash`.
6. `everything done? also use rich` — added a `ui.py` Rich console and moved the
   demo's presentation onto it: section rules, an agent-reply panel, a triage
   table, a guardrail-results table, a coloured audit trail, and a red "cannot
   start" panel for a missing key. Logic modules stay output-free. Also added a
   `.gitattributes` to normalise line endings to LF.
7. `leave it we will use openaikey` — made OpenAI the real model. `config.py` now
   prefers `OPENAI_API_KEY` (`gpt-4o-mini`) and keeps `GEMINI_API_KEY` as an
   automatic fallback to `gemini-2.5-flash`. Ran the full demo live on OpenAI and
   committed the resulting `saved.json` (L001 + L004, both priority=high).

8. `make ui also` -> `Web app (FastAPI + page)` — added `web.py` (a thin FastAPI
   layer: `/api/triage`, `/api/saved`, `/api/reset`, `/api/meta`) and
   `static/index.html`, a theme-aware single page that POSTs an inquiry and
   renders the typed verdict + save status. `realty-desk-web` script entry.
9. `change the author name to muhammadumerakmal` — updated `pyproject.toml`
   `authors` and the local `git config user.name`.

## Amendment

_(Record a late spec change and the one-line request that absorbed it here.)_
