"""Lookup tools — Task 1, reading from context per Task 2.

Both tools take ``wrapper: RunContextWrapper[AgencyProfile]`` as their first
parameter. The SDK fills that from the run's ``context=`` and removes it from the
JSON schema the model sees (verify with ``lookup_listing_availability.params_json_schema``).
No module-level agency data is read here.

Tool docstrings are written *for the model*: they say when to call the tool and
what not to do with the result.
"""

from __future__ import annotations

from agents import RunContextWrapper, function_tool

from realty_desk.context import AgencyProfile
from realty_desk.hooks import audit_args


@function_tool
async def lookup_listing_availability(
    wrapper: RunContextWrapper[AgencyProfile],
    area: str | None = None,
    listing_type: str | None = None,
) -> str:
    """Check the agency's real inventory for listings matching a client's request.

    Call this BEFORE you quote, estimate, or discuss any price. Pass the client's
    requested `area` (e.g. "DHA Phase 5") and/or `listing_type` (e.g. "3-bed
    rental", "10 marla house", "plot"). Returns the matching listings with their
    public asking price range in PKR.

    If nothing matches, the result says so — in that case tell the client we have
    no matching inventory. Never invent a listing, an address, or a price.
    """
    audit_args("lookup_listing_availability", area=area, listing_type=listing_type)
    profile = wrapper.context
    matches = profile.find_listings(area=area, listing_type=listing_type)

    if not area and not listing_type:
        return "No area or listing type given. Ask the client which area and property type they want."

    query = " / ".join(part for part in (area, listing_type) if part)
    if not matches:
        return (
            f"No active listings match '{query}'. {profile.agency_name} has nothing to offer here. "
            f"Tell the client that; do not quote a price or describe a property."
        )

    prices = [m.asking_price_pkr for m in matches]
    lines = [
        f"- {m.id}: {m.type} in {m.area}, asking PKR {m.asking_price_pkr:,}"
        for m in matches
    ]
    return (
        f"{len(matches)} listing(s) match '{query}':\n"
        + "\n".join(lines)
        + f"\nPublic asking price range: PKR {min(prices):,} to PKR {max(prices):,}."
    )


@function_tool
async def check_agent_availability(
    wrapper: RunContextWrapper[AgencyProfile],
    week: str,
) -> str:
    """Check which agents have open slots in a given `week` (e.g. "this week",
    "week of 15 Sept"). Use this when the client wants a viewing or a callback
    time. Returns each agent and their free hours; an agent with 0 free hours
    cannot take the appointment.
    """
    audit_args("check_agent_availability", week=week)
    profile = wrapper.context
    free = {name: hrs for name, hrs in profile.agent_hours_free_per_week.items() if hrs > 0}
    if not free:
        return f"{week}: no agent has open slots. Offer the client a call instead of a viewing."
    parts = ", ".join(f"{name} ({hrs} hr free)" for name, hrs in free.items())
    return f"{week}: {parts}."
