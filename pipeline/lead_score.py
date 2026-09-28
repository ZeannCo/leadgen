"""Lead score (0-100) for prioritizing enrichment and dial queues.

v2 rewards value first: estimated rent dominates the score, with name
match-likelihood and freshness as secondary ordering signals. Priority ZIP tier
still sorts outside the score in the queue builders.
"""
from __future__ import annotations

from datetime import date

from services.name_utils import clean_tenant_name, is_common_surname, parse_name

# Weight profiles (w_rent/w_match/w_fresh must sum to 100) + value floor/cap per
# business. NOTE: `rent`/`rent_floor`/`rent_cap` are really the VALUE-AMOUNT
# dimension — market rent for eviction businesses, debt amount for Claim Services, and
# unused (w_rent=0) for Judgment Services which has no amount.
_PROFILES = {
    "resident": dict(w_rent=50, w_match=30, w_fresh=20, rent_floor=800.0, rent_cap=3500.0),
    # Judgment Review: judgments don't time-decay like pre-court filings and cluster near the
    # rent floor, so drop freshness (-> rent+match) and lower the floor for spread.
    "judgment_review":    dict(w_rent=60, w_match=40, w_fresh=0,  rent_floor=1200.0, rent_cap=3500.0),
    # Claim Services (debt x filed): value = debt amount; freshness matters (the ~30-day
    # Answer window before default judgment). Floor/cap span typical debt-claim sizes.
    "claims":  dict(w_rent=50, w_match=30, w_fresh=20, rent_floor=1000.0, rent_cap=25000.0),
    # Judgment Services (debt x judgment): no amount dimension, so weight name match +
    # writ freshness only (freshest writ = most urgent exemption window).
    "judgment": dict(w_rent=0, w_match=50, w_fresh=50, rent_floor=0.0, rent_cap=1.0),
}
_COMMON_SURNAME_FACTOR = 0.55


def _clamp(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def score_lead(
    *,
    rent,
    tenant_name: str,
    lead_date: date | None,
    today: date,
    fresh_window_days: int = 21,
    profile: str = "resident",
) -> int:
    """Return a 0-100 lead score using the named weight profile.

    rent is a market rent estimate; None contributes 0 rent points. lead_date is
    filing_date for Resident Services and judgment_date for Judgment Review.
    """
    p = _PROFILES[profile]

    rent_pts = 0.0
    if rent:
        rent_pts = p["w_rent"] * _clamp(
            (float(rent) - p["rent_floor"]) / (p["rent_cap"] - p["rent_floor"])
        )

    first, last = parse_name(clean_tenant_name(tenant_name or ""))
    common = bool(last and is_common_surname(last))
    match_pts = p["w_match"] * (_COMMON_SURNAME_FACTOR if common else 1.0)

    if lead_date is None or not p["w_fresh"]:
        fresh_pts = 0.0
    else:
        age = (today - lead_date).days
        fresh_pts = p["w_fresh"] * _clamp((fresh_window_days - age) / fresh_window_days)

    return max(0, min(100, round(rent_pts + match_pts + fresh_pts)))

