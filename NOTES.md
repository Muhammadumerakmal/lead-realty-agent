# NOTES.md

One line per task: what broke first, what changed.

- **Task 0** — `uv init` pinned `requires-python = ">=3.14"` and a `realty_desk:main` script entry; lowered to `>=3.13` and pointed the entry at `realty_desk.main:main`, and made a missing key raise `SystemExit("...copy .env.example...")` so it prints a message, not a traceback.
- **Task 1** — tools first returned dicts; switched to preformatted strings so the model reads inventory directly, and made `find_listings` return `[]` for an empty query so the tool tells the model to ask for area/type instead of guessing.
- **Task 2** — `Agent(model=...)` type-checks at construction so a stub model won't load; used `model=None` for the offline wiring check and confirmed `lookup_listing_availability.params_json_schema` exposes only `area` / `listing_type` — the SDK strips `wrapper` itself.
- **Task 3** — `saved.json` was resolved against the caller's cwd; fixed it to project root via `Path(__file__).resolve().parents[2]`, and the save banner runs `int(budget_pkr * 1.05)` to prove the field is a real int.
- **Task 4** — the first regex set also caught ordinary price questions; tightened it so "lowest the seller will accept" and "hide the seepage / inflate the footage" trip while "2-bed in Johar Town around 90k" does not — checked against all 6 fixtures, zero false positives.
- **Task 5** — `on_tool_start` carries no tool arguments in Agents SDK 0.22, so each tool calls `audit_args()` on entry (armed only for the Task 5 run) and `AuditHooks` numbers calls in request order for the args + result log.
