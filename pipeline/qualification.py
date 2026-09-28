from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


DEFAULT_RENT_THRESHOLD = Decimal("1800")
STATE_RENT_THRESHOLDS: dict[str, Decimal] = {
    "TX": Decimal("1500"),
    "TN": Decimal("1600"),
    "GA": Decimal("1600"),
    "FL": Decimal("1800"),
    "IL": Decimal("1800"),
    "WA": Decimal("1900"),
    "AZ": Decimal("1500"),
    "NV": Decimal("1600"),
}
FRESH_FILING_DAYS = 7

# Illustrative demo policy, not a client targeting configuration.
APPROVED_ZIPS: dict[str, set[str]] = {"TN": {"37211"}}

_ZIP_RE = re.compile(r"\b(\d{5})(?:-\d{4})?\b")
_COMMERCIAL_TYPES = {"commercial", "retail", "office"}


@dataclass(frozen=True)
class QualificationOutcome:
    property_zip: str | None
    lead_bucket: str
    discard_reason: str | None
    qualification_notes: str


def extract_property_zip(address: str) -> str | None:
    matches = _ZIP_RE.findall(address or "")
    return matches[-1] if matches else None


def is_approved_zip(state: str, property_zip: str | None) -> bool:
    if not property_zip:
        return False
    return property_zip in APPROVED_ZIPS.get(state.upper(), set())


def rent_threshold_for_state(state: str) -> Decimal:
    return STATE_RENT_THRESHOLDS.get(state.upper(), DEFAULT_RENT_THRESHOLD)


def classify_lead(
    *,
    state: str,
    property_address: str,
    filing_date: date,
    property_type: str | None = None,
    estimated_rent: float | Decimal | None = None,
    today: date | None = None,
    capture_expanded: bool = False,
    bypass_zip_filter: bool = False,
) -> QualificationOutcome:
    """Classify a filing into a lead_bucket.

    Phase 1 (2026-06-10) removed three gates that were dropping tenant leads:
      - ZIP allowlist  — was landlord-affluence calibrated, not tenant demographics
      - rent threshold — rent is now a PRIORITY signal (Rentometer), never a discard
      - 7-day 'held'   — freshness is enforced by good_leads_now, not classification

    What remains is data-quality + type routing only:
      - missing ZIP  -> discarded (until Phase 2 self-heal)
      - commercial   -> commercial
      - else         -> residential_approved

    `capture_expanded` / `bypass_zip_filter` are retained for caller compatibility
    (pipeline.runner passes them from env) but are now no-ops.
    """
    property_zip = extract_property_zip(property_address)
    if property_zip is None:
        return QualificationOutcome(
            property_zip=None,
            lead_bucket="discarded",
            discard_reason="missing_zip",
            qualification_notes="Discarded before enrichment: no property ZIP found.",
        )

    normalized_type = (property_type or "").strip().lower()
    if normalized_type in _COMMERCIAL_TYPES:
        return QualificationOutcome(
            property_zip=property_zip,
            lead_bucket="commercial",
            discard_reason=None,
            qualification_notes="Commercial lead: high priority.",
        )

    return QualificationOutcome(
        property_zip=property_zip,
        lead_bucket="residential_approved",
        discard_reason=None,
        qualification_notes="Approved residential tenant lead.",
    )
