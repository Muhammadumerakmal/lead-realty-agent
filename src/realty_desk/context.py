"""Private agency data — Task 2.

Everything here is supplied to a run as ``context``. The Agents SDK passes the
context object to *tool code* (via ``RunContextWrapper``) but strips it from the
JSON schema the model sees. So ``seller_min_price_pkr`` can drive tool logic
while being structurally unreachable by the model or a prompt-injection attack.

Nothing in this module is ever formatted into an instruction or a message that
goes to the model.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


def _tokens(text: str) -> list[str]:
    """Lowercase word tokens, punctuation dropped ('DHA Phase 5, Lahore' -> [dha, phase, 5, lahore])."""
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower()).split()


@dataclass
class Listing:
    """One property on the agency's books."""

    id: str
    area: str
    type: str  # e.g. "10 marla house", "3-bed rental", "5 marla plot"
    asking_price_pkr: int  # public — may be quoted to a client
    seller_min_price_pkr: int  # PRIVATE — negotiating leverage, never leaves this process
    known_issues: list[str] = field(default_factory=list)  # PRIVATE — disclosed only in person


@dataclass
class AgencyProfile:
    """The run context: who we are, what we hold, who is free, are we licensed."""

    agency_name: str
    listings: list[Listing]
    agent_hours_free_per_week: dict[str, int]  # agent name -> open hours this week
    licensed: bool

    def find_listings(self, *, area: str | None = None, listing_type: str | None = None) -> list[Listing]:
        """Token match on area and/or type, punctuation-insensitive. Empty query -> no match.

        A listing matches when every query token appears in the listing's tokens, so
        "DHA Phase 5 Lahore" still matches "DHA Phase 5, Lahore" and "10 marla house"
        matches "10 marla house".
        """
        if not area and not listing_type:
            return []
        area_q = _tokens(area or "")
        type_q = _tokens(listing_type or "")
        out: list[Listing] = []
        for listing in self.listings:
            if area_q and not all(tok in _tokens(listing.area) for tok in area_q):
                continue
            if type_q and not all(tok in _tokens(listing.type) for tok in type_q):
                continue
            out.append(listing)
        return out


def sample_agency() -> AgencyProfile:
    """Fixture agency used by the demo. Prices in PKR."""
    return AgencyProfile(
        agency_name="Meezan Realty (Lahore & Islamabad)",
        listings=[
            Listing(
                id="DHA5-10M-01",
                area="DHA Phase 5, Lahore",
                type="10 marla house",
                asking_price_pkr=55_000_000,
                seller_min_price_pkr=49_500_000,
                known_issues=["boundary wall seepage on the north side"],
            ),
            Listing(
                id="BHR-5M-07",
                area="Bahria Town, Lahore",
                type="5 marla house",
                asking_price_pkr=30_000_000,
                seller_min_price_pkr=27_000_000,
                known_issues=[],
            ),
            Listing(
                id="F7-KANAL-02",
                area="F-7, Islamabad",
                type="1 kanal house",
                asking_price_pkr=210_000_000,
                seller_min_price_pkr=190_000_000,
                known_issues=["kitchen needs full renovation"],
            ),
            Listing(
                id="ISB-3BED-RENT-04",
                area="G-11, Islamabad",
                type="3-bed rental",
                asking_price_pkr=250_000,  # per month
                seller_min_price_pkr=225_000,
                known_issues=[],
            ),
            Listing(
                id="LHR-2BED-RENT-09",
                area="Johar Town, Lahore",
                type="2-bed rental",
                asking_price_pkr=95_000,  # per month
                seller_min_price_pkr=85_000,
                known_issues=["no dedicated parking"],
            ),
        ],
        agent_hours_free_per_week={"Sana": 6, "Bilal": 2, "Imran": 0},
        licensed=True,
    )
